#!/usr/bin/env python3
"""
BookMyShow Monitor using CloudScraper to bypass anti-bot protection
"""

import time
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import json

# Try to import cloudscraper, fallback to requests if not available
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    import requests
    CLOUDSCRAPER_AVAILABLE = False
    print("Warning: cloudscraper not installed. Install with: pip install cloudscraper")

from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class CloudScraperMonitor:
    def __init__(self):
        # Use cloudscraper if available, otherwise fallback to requests
        if CLOUDSCRAPER_AVAILABLE:
            logger.info("Using CloudScraper for anti-bot bypass")
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'linux',
                    'desktop': True
                },
                delay=10  # Delay between requests
            )
        else:
            logger.warning("CloudScraper not available, using standard requests")
            self.scraper = requests.Session()
            self.scraper.headers.update({
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
        
        self.target_screens = [
            "PVR Soul Spirit",
            "PVR Centro Mall",
            "PVR Nexus Koramangala",
            "PVR Felicity Mall"
        ]
        
        # Multiple URLs to try
        self.urls = [
            "https://in.bookmyshow.com/bengaluru/movies",
            "https://in.bookmyshow.com/explore/movies-bengaluru",
            "https://in.bookmyshow.com/bengaluru/movies/coolie-ET00395817"
        ]
        
        self.email_config = {
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'email': os.getenv('EMAIL_USER', os.getenv('EMAIL_FROM')),
            'password': os.getenv('EMAIL_PASSWORD'),
            'to_email': os.getenv('EMAIL_TO')
        }

    def check_availability(self):
        """Check ticket availability using CloudScraper"""
        
        for url in self.urls:
            try:
                logger.info(f"Checking URL: {url}")
                
                # CloudScraper handles anti-bot challenges automatically
                response = self.scraper.get(url, timeout=30)
                
                logger.info(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_text = soup.get_text().lower()
                    
                    # Check for Coolie movie
                    if 'coolie' in page_text:
                        logger.info("✅ Found Coolie movie on page")
                        
                        # Check for PVR screens
                        screens_found = []
                        for screen in self.target_screens:
                            if screen.lower() in page_text:
                                screens_found.append(screen)
                                logger.info(f"🎯 Target screen found: {screen}")
                        
                        if screens_found:
                            return screens_found
                    else:
                        logger.info("Movie 'Coolie' not found on this page")
                        
                elif response.status_code == 403:
                    logger.warning(f"403 Forbidden - CloudScraper couldn't bypass protection for {url}")
                else:
                    logger.warning(f"Unexpected status code: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error checking {url}: {e}")
                
        return []

    def send_alert(self, screens_found):
        """Send email alert"""
        if not self.email_config['email'] or not self.email_config['to_email']:
            logger.warning("Email configuration incomplete")
            return
        
        try:
            subject = f"🎬 Coolie - {len(screens_found)} Target Screens Detected!"
            
            body = f"""
🎬 COOLIE TICKET MONITOR ALERT 🎬

Target screens detected on BookMyShow:

"""
            for screen in screens_found:
                body += f"✅ {screen}\n"
            
            body += f"""

Check BookMyShow now:
• https://in.bookmyshow.com/bengaluru/movies
• Search for "Coolie" movie

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Note: Automated detection successful. Please verify manually.
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
            
            logger.info("📧 Alert email sent!")
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    def run(self):
        """Run the monitor"""
        logger.info("=" * 60)
        logger.info("🎬 COOLIE TICKET MONITOR (CloudScraper)")
        logger.info("=" * 60)
        
        screens = self.check_availability()
        
        if screens:
            logger.info(f"✅ SUCCESS! Found {len(screens)} target screens")
            self.send_alert(screens)
            return True
        else:
            logger.info("⏳ No target screens found yet")
            return False

def main():
    monitor = CloudScraperMonitor()
    success = monitor.run()
    
    # Exit with 0 to not fail GitHub Actions
    import sys
    sys.exit(0)

if __name__ == "__main__":
    main()