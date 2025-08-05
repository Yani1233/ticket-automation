"""Core ticket monitoring functionality"""

import os
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional
import yaml
from .notifiers import EmailNotifier

logger = logging.getLogger(__name__)

class TicketAlert:
    def __init__(self, config_path: str = 'config.yaml'):
        self.config = self.load_config(config_path)
        self.state_file = 'state.json'
        self.session = requests.Session()
        # More comprehensive headers to avoid 403 errors
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })

    def load_config(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Load environment variables
            for key, value in config.get('email', {}).items():
                if isinstance(value, str) and value.startswith('ENV:'):
                    env_var = value.replace('ENV:', '')
                    config['email'][key] = os.getenv(env_var, '')
            
            return config
        except FileNotFoundError:
            logger.error(f"Config file {config_path} not found")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            raise

    def load_state(self) -> Dict:
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'alerted_platforms': [], 'last_check': None}

    def save_state(self, state: Dict):
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def check_platform(self, platform: Dict) -> bool:
        platform_name = platform['name']
        url = platform['url']
        selector = platform['selector']
        
        try:
            logger.info(f"Checking {platform_name}...")
            
            # Add platform-specific headers if needed
            headers = self.session.headers.copy()
            if 'bookmyshow' in url:
                headers['Referer'] = 'https://in.bookmyshow.com/'
            elif 'pvrcinemas' in url:
                headers['Referer'] = 'https://www.pvrcinemas.com/'
            
            response = self.session.get(url, headers=headers, timeout=15)
            
            # Handle 403 specifically
            if response.status_code == 403:
                logger.warning(f"{platform_name} returned 403 Forbidden - site may be blocking automated requests")
                # Try with a small delay and different headers
                time.sleep(2)
                headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                response = self.session.get(url, headers=headers, timeout=15)
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if booking is available based on selector
            if platform['detection_method'] == 'element_exists':
                elements = soup.select(selector)
                for element in elements:
                    element_text = element.get_text().lower()
                    # Look for actual booking availability, not just "notify me"
                    if any(keyword in element_text for keyword in ['book tickets', 'book now', 'showtimes']):
                        logger.info(f"🎬 TICKETS AVAILABLE on {platform_name}!")
                        return True
                    elif 'notify me' in element_text or 'coming soon' in element_text:
                        logger.info(f"{platform_name}: Movie found but only 'Notify Me' available")
                        return False
            
            elif platform['detection_method'] == 'text_contains':
                # First check if the movie is mentioned on the page
                page_text = soup.get_text().lower()
                movie_found = any(keyword.lower() in page_text for keyword in ['coolie'])
                
                if movie_found:
                    logger.info(f"Found 'Coolie' mentioned on {platform_name}")
                    # Now check for booking availability
                    elements = soup.select(selector)
                    for element in elements:
                        element_text = element.get_text().lower()
                        if any(keyword.lower() in element_text 
                              for keyword in platform.get('keywords', ['book', 'tickets'])):
                            # Check if this element is related to Coolie
                            parent_text = element.parent.get_text().lower() if element.parent else element_text
                            if 'coolie' in parent_text:
                                logger.info(f"🎬 TICKETS AVAILABLE on {platform_name}!")
                                return True
                else:
                    logger.info(f"Movie 'Coolie' not found on {platform_name} yet")
            
            logger.info(f"{platform_name}: No tickets available yet")
            return False
            
        except requests.RequestException as e:
            logger.error(f"Error checking {platform_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking {platform_name}: {e}")
            return False

    def send_email_alert(self, platform_name: str, url: str):
        """Send email alert using EmailNotifier"""
        email_notifier = EmailNotifier(self.config['email'])
        email_notifier.send(platform_name, url)

    def run_check(self):
        state = self.load_state()
        platforms = self.config['platforms']
        
        logger.info("Starting ticket availability check...")
        
        tickets_found = False
        
        for platform in platforms:
            platform_name = platform['name']
            
            # Skip if already alerted for this platform
            if platform_name in state['alerted_platforms']:
                logger.info(f"Already alerted for {platform_name}, skipping...")
                continue
            
            if self.check_platform(platform):
                self.send_email_alert(platform_name, platform['url'])
                state['alerted_platforms'].append(platform_name)
                tickets_found = True
        
        state['last_check'] = datetime.now().isoformat()
        self.save_state(state)
        
        if tickets_found:
            logger.info("🎉 Tickets found! Alerts sent. Stopping monitoring.")
            return True
        else:
            logger.info("No tickets available yet. Will check again later.")
            return False

    def run_continuous(self):
        interval_minutes = self.config.get('check_interval_minutes', 30)
        
        logger.info(f"Starting continuous monitoring (checking every {interval_minutes} minutes)")
        
        while True:
            try:
                if self.run_check():
                    break
                
                logger.info(f"Sleeping for {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    import sys
    
    alert_system = TicketAlert()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        alert_system.run_check()
    else:
        alert_system.run_continuous()