#!/usr/bin/env python3
"""
BookMyShow Monitor with Proxy Support
Uses free proxy services to bypass IP-based blocking
"""

import requests
import time
import logging
import random
from bs4 import BeautifulSoup
from datetime import datetime
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ProxyBookMyShowMonitor:
    def __init__(self):
        self.target_screens = [
            "PVR Soul Spirit",
            "PVR Centro Mall",
            "PVR Nexus Koramangala",
            "PVR Felicity Mall"
        ]
        
        # Free proxy services (use cautiously)
        self.proxy_list = self.get_free_proxies()
        
        self.email_config = {
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'email': os.getenv('EMAIL_USER', os.getenv('EMAIL_FROM')),
            'password': os.getenv('EMAIL_PASSWORD'),
            'to_email': os.getenv('EMAIL_TO')
        }

    def get_free_proxies(self):
        """Get a list of free proxies (for testing only)"""
        # In production, use a reliable proxy service
        # These are example proxies - they may not work
        proxies = []
        
        # Try to fetch from free proxy API
        try:
            response = requests.get('https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=yes&anonymity=elite', timeout=5)
            if response.status_code == 200:
                proxy_lines = response.text.strip().split('\n')
                for line in proxy_lines[:5]:  # Use only first 5
                    if ':' in line:
                        proxies.append(f'http://{line.strip()}')
                logger.info(f"Found {len(proxies)} free proxies")
        except:
            pass
        
        # If no proxies found, return None (will use direct connection)
        return proxies if proxies else [None]

    def make_request_with_proxy(self, url, proxy=None):
        """Make request using proxy"""
        headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        proxies_dict = {'http': proxy, 'https': proxy} if proxy else None
        
        try:
            if proxy:
                logger.info(f"Using proxy: {proxy}")
            else:
                logger.info("Using direct connection")
                
            response = requests.get(
                url, 
                headers=headers, 
                proxies=proxies_dict,
                timeout=15,
                verify=False  # Disable SSL verification for proxies
            )
            
            logger.info(f"Response status: {response.status_code}")
            return response
            
        except Exception as e:
            logger.error(f"Request failed with proxy {proxy}: {e}")
            return None

    def check_availability(self):
        """Check ticket availability using multiple proxies"""
        urls = [
            "https://in.bookmyshow.com/bengaluru/movies",
            "https://in.bookmyshow.com/explore/movies-bengaluru"
        ]
        
        screens_found = []
        
        for url in urls:
            logger.info(f"Checking URL: {url}")
            
            # Try each proxy
            for proxy in self.proxy_list:
                response = self.make_request_with_proxy(url, proxy)
                
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_text = soup.get_text().lower()
                    
                    # Check for Coolie movie
                    if 'coolie' in page_text:
                        logger.info("✅ Found Coolie movie!")
                        
                        # Check for target screens
                        for screen in self.target_screens:
                            if screen.lower() in page_text:
                                if screen not in screens_found:
                                    screens_found.append(screen)
                                    logger.info(f"🎯 Target screen found: {screen}")
                        
                        # If we found the movie, no need to try more proxies
                        break
                        
                elif response and response.status_code == 403:
                    logger.warning(f"403 Forbidden with proxy {proxy}")
                    
                # Add delay between requests
                time.sleep(random.uniform(2, 5))
                
        return screens_found

    def send_alert(self, screens_found):
        """Send email alert"""
        if not self.email_config['email'] or not self.email_config['to_email']:
            logger.warning("Email configuration incomplete")
            return
        
        try:
            subject = f"🎬 Coolie - Screens Detected (Proxy Check)"
            
            body = f"""
🎬 COOLIE TICKET ALERT 🎬

Proxy-based check found mentions of:

"""
            for screen in screens_found:
                body += f"✅ {screen}\n"
            
            body += f"""

Check BookMyShow:
https://in.bookmyshow.com/bengaluru/movies

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Note: Detection via proxy network. Please verify manually.
"""
            
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = self.email_config['to_email']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            server.sendmail(self.email_config['email'], self.email_config['to_email'], msg.as_string())
            server.quit()
            
            logger.info("📧 Alert sent!")
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    def run(self):
        """Run the monitor"""
        logger.info("=" * 60)
        logger.info("🎬 COOLIE MONITOR (Proxy-based)")
        logger.info("=" * 60)
        
        # Suppress SSL warnings for proxy connections
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        screens = self.check_availability()
        
        if screens:
            logger.info(f"✅ Found {len(screens)} target screens")
            self.send_alert(screens)
            return True
        else:
            logger.info("⏳ No target screens found")
            return False

def main():
    monitor = ProxyBookMyShowMonitor()
    monitor.run()
    
    import sys
    sys.exit(0)

if __name__ == "__main__":
    main()