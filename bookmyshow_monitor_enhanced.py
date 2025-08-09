#!/usr/bin/env python3
"""
Enhanced BookMyShow Ticket Monitor with Anti-Bot Bypass
Monitors ticket availability for Coolie movie in preferred PVR screens in Bengaluru
"""

import requests
import time
import logging
import random
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure logging for GitHub Actions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only console output for GitHub Actions
    ]
)
logger = logging.getLogger(__name__)

class EnhancedBookMyShowMonitor:
    def __init__(self):
        self.session = requests.Session()
        
        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ]
        
        # Enhanced headers to mimic real browser
        self.update_session_headers()
        
        # Target screens - your preferred PVR locations
        self.target_screens = [
            "PVR Soul Spirit",
            "PVR Centro Mall", 
            "PVR Nexus Koramangala",
            "PVR Felicity Mall"
        ]
        
        # BookMyShow URLs - try multiple endpoints
        self.urls = [
            "https://in.bookmyshow.com/movies/bengaluru/coolie/buytickets/ET00395817/20250814",
            "https://in.bookmyshow.com/bengaluru/movies/coolie-ET00395817",
            "https://in.bookmyshow.com/bengaluru/movies"
        ]
        
        # Email configuration
        self.email_config = {
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'email': os.getenv('EMAIL_USER'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'to_email': os.getenv('EMAIL_TO')
        }
        
        # Request retry configuration
        self.max_retries = 3
        self.retry_delay = 2

    def update_session_headers(self):
        """Update session with rotating headers"""
        user_agent = random.choice(self.user_agents)
        
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Cache-Control': 'max-age=0',
            'Pragma': 'no-cache',
            'DNT': '1'
        })

    def make_request_with_retry(self, url, method='GET', **kwargs):
        """Make HTTP request with retry logic and anti-bot measures"""
        for attempt in range(self.max_retries):
            try:
                # Update headers for each request
                self.update_session_headers()
                
                # Add random delay to mimic human behavior
                if attempt > 0:
                    delay = self.retry_delay * (2 ** attempt) + random.uniform(0.5, 2)
                    logger.info(f"Waiting {delay:.1f} seconds before retry {attempt + 1}...")
                    time.sleep(delay)
                
                # Set proper referer
                if 'headers' not in kwargs:
                    kwargs['headers'] = {}
                kwargs['headers']['Referer'] = 'https://in.bookmyshow.com/'
                
                # Make request
                if method == 'GET':
                    response = self.session.get(url, timeout=30, **kwargs)
                else:
                    response = self.session.post(url, timeout=30, **kwargs)
                
                logger.info(f"Response status: {response.status_code} (Attempt {attempt + 1}/{self.max_retries})")
                
                # Handle different response codes
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    logger.warning(f"403 Forbidden - Trying alternative approach...")
                    # Try with cookies if available
                    if attempt == 0:
                        self.try_get_cookies()
                elif response.status_code == 429:
                    logger.warning(f"429 Too Many Requests - Rate limited")
                    time.sleep(10)  # Wait longer for rate limit
                elif response.status_code >= 500:
                    logger.warning(f"{response.status_code} Server Error")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error (Attempt {attempt + 1}): {e}")
                
        return None

    def try_get_cookies(self):
        """Try to get cookies from main page first"""
        try:
            logger.info("Attempting to get cookies from main page...")
            # First visit the main page
            main_response = self.session.get('https://in.bookmyshow.com/', timeout=10)
            if main_response.status_code == 200:
                logger.info("Got cookies from main page")
                # Visit movies page
                movies_response = self.session.get('https://in.bookmyshow.com/explore/movies-bengaluru', timeout=10)
                if movies_response.status_code == 200:
                    logger.info("Successfully navigated to movies page")
        except Exception as e:
            logger.warning(f"Could not get cookies: {e}")

    def try_api_endpoint(self):
        """Try to fetch data from BookMyShow API endpoints"""
        try:
            logger.info("Trying API endpoint approach...")
            
            # BookMyShow API endpoints (these might work better than scraping)
            api_urls = [
                "https://in.bookmyshow.com/api/movies/coolie/ET00395817",
                "https://in.bookmyshow.com/serv/getData?cmd=GETTRAILERS&mtype=cs&msrch=coolie"
            ]
            
            for api_url in api_urls:
                response = self.make_request_with_retry(
                    api_url,
                    headers={
                        'Accept': 'application/json, text/plain, */*',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                )
                
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        logger.info(f"Got API response: {json.dumps(data, indent=2)[:500]}")
                        return data
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"API approach failed: {e}")
        
        return None

    def check_screen_availability(self):
        """Check if tickets are available in target screens with multiple approaches"""
        
        # Try API first
        api_data = self.try_api_endpoint()
        if api_data:
            return self.parse_api_response(api_data)
        
        # Try web scraping with enhanced anti-bot measures
        for url in self.urls:
            try:
                logger.info(f"🎬 Checking BookMyShow URL: {url}")
                logger.info(f"Target screens: {', '.join(self.target_screens)}")
                
                response = self.make_request_with_retry(url)
                
                if not response:
                    logger.error(f"Failed to get response from {url}")
                    continue
                
                if response.status_code != 200:
                    logger.error(f"Non-200 status code: {response.status_code}")
                    # Try next URL
                    continue
                
                # Parse response
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text()
                
                # Log page title for verification
                title = soup.find('title')
                if title:
                    logger.info(f"Page title: {title.get_text().strip()}")
                
                # Check if we got a valid page
                if 'coolie' in page_text.lower() or 'pvr' in page_text.lower():
                    logger.info("Found relevant content on page")
                    available_screens = self.extract_available_screens(soup, page_text)
                    
                    if available_screens:
                        return self.filter_target_screens(available_screens)
                
            except Exception as e:
                logger.error(f"Error checking {url}: {e}")
                continue
        
        logger.warning("All approaches failed - BookMyShow might be blocking automated requests")
        return {}

    def parse_api_response(self, data):
        """Parse API response for screen availability"""
        available_screens = {}
        
        try:
            # Parse based on API response structure
            # This would need to be adapted based on actual API response
            logger.info("Parsing API response for screen information...")
            
        except Exception as e:
            logger.error(f"Error parsing API response: {e}")
        
        return available_screens

    def extract_available_screens(self, soup, page_text):
        """Extract available screens from page content"""
        available_screens = {}
        all_text_lower = page_text.lower()
        
        logger.info("🔍 Extracting screen information from page...")
        
        # Look for PVR screens
        pvr_screens = {
            'soul spirit': 'PVR Soul Spirit Central Mall, Bellandur',
            'centro': 'PVR Centro Mall',
            'nexus koramangala': 'PVR Nexus Koramangala',
            'felicity': 'PVR Felicity Mall'
        }
        
        for pvr_key, pvr_name in pvr_screens.items():
            if pvr_key in all_text_lower or pvr_name.lower() in all_text_lower:
                logger.info(f"Found {pvr_name} on page")
                available_screens[pvr_name] = {
                    'status': 'DETECTED',
                    'source': 'page_scan'
                }
        
        return available_screens

    def filter_target_screens(self, available_screens):
        """Filter for target screens only"""
        matching_screens = {}
        
        for screen_name, details in available_screens.items():
            if any(target.lower() in screen_name.lower() for target in self.target_screens):
                matching_screens[screen_name] = details
                logger.info(f"✅ Target screen matched: {screen_name}")
        
        return matching_screens

    def send_alert(self, matching_screens):
        """Send email alert for available screens"""
        if not self.email_config['email'] or not self.email_config['to_email']:
            logger.warning("Email configuration incomplete - skipping email alert")
            return
        
        try:
            subject = f"🎬 COOLIE Target Screens Detected - {len(matching_screens)} Locations"
            
            body = f"""
🎉 COOLIE TICKET MONITOR UPDATE 🎉

Found: {len(matching_screens)} of your preferred screens

TARGET SCREENS DETECTED:
"""
            
            for screen_name, details in matching_screens.items():
                body += f"🎯 {screen_name}\n"
                body += f"   Status: {details.get('status', 'DETECTED')}\n\n"
            
            body += f"""
📱 BOOKING URLS: 
• {self.urls[0]}
• https://in.bookmyshow.com/bengaluru/movies

⏰ Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Note: BookMyShow may be blocking automated access. Please check manually.

Your Preferred PVR Screens:
• PVR Soul Spirit
• PVR Centro Mall  
• PVR Nexus Koramangala
• PVR Felicity Mall

Happy Booking! 🎬✨
"""
            
            # Send email
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = self.email_config['to_email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            text = msg.as_string()
            server.sendmail(self.email_config['email'], self.email_config['to_email'], text)
            server.quit()
            
            logger.info("📧 Email alert sent successfully!")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

    def run_once(self):
        """Run a single check"""
        logger.info("=" * 60)
        logger.info("🎬 ENHANCED COOLIE TICKET MONITOR")
        logger.info("=" * 60)
        
        matching_screens = self.check_screen_availability()
        
        if matching_screens:
            logger.info(f"🎉 Found {len(matching_screens)} target screens!")
            self.send_alert(matching_screens)
            return True
        else:
            logger.info("⏳ No target screens detected yet")
            # Don't fail completely if blocked
            return False

def main():
    """Main function"""
    import sys
    
    monitor = EnhancedBookMyShowMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        success = monitor.run_once()
        # Exit with 0 even if no screens found (to avoid failing GitHub Actions)
        sys.exit(0)
    else:
        success = monitor.run_once()
        sys.exit(0)

if __name__ == "__main__":
    main()