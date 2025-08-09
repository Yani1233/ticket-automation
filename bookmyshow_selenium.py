#!/usr/bin/env python3
"""
BookMyShow Monitor using Selenium with Undetected ChromeDriver
This approach uses a real browser to bypass anti-bot protection
"""

import time
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Warning: Selenium/undetected-chromedriver not installed")

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

class SeleniumBookMyShowMonitor:
    def __init__(self):
        self.driver = None
        self.target_screens = [
            "PVR Soul Spirit",
            "PVR Centro Mall",
            "PVR Nexus Koramangala"
        ]
        
        self.email_config = {
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'email': os.getenv('EMAIL_USER', os.getenv('EMAIL_FROM')),
            'password': os.getenv('EMAIL_PASSWORD'),
            'to_email': os.getenv('EMAIL_TO')
        }

    def setup_driver(self):
        """Setup undetected Chrome driver"""
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not available")
            return False
        
        try:
            options = uc.ChromeOptions()
            
            # Headless mode for GitHub Actions
            if os.getenv('GITHUB_ACTIONS'):
                options.add_argument('--headless=new')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-software-rasterizer')
                
            # Additional options to avoid detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Try different driver initialization methods
            try:
                # Try undetected-chromedriver first
                self.driver = uc.Chrome(options=options, version_main=None)  # Auto-detect version
            except:
                try:
                    # Fallback to standard Chrome with custom binary location
                    if os.getenv('GITHUB_ACTIONS'):
                        options.binary_location = '/usr/bin/chromium-browser'
                    self.driver = uc.Chrome(options=options, driver_executable_path='/usr/bin/chromedriver')
                except:
                    # Last resort: use base Selenium
                    from selenium import webdriver
                    self.driver = webdriver.Chrome(options=options)
            
            logger.info("✅ Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup driver: {e}")
            logger.error("Try installing: sudo apt-get install chromium-browser chromium-chromedriver")
            return False

    def check_availability(self):
        """Check ticket availability using Selenium"""
        if not self.setup_driver():
            return []
        
        screens_found = []
        
        try:
            # Visit BookMyShow Bengaluru movies page
            logger.info("Navigating to BookMyShow...")
            self.driver.get("https://in.bookmyshow.com/explore/movies-bengaluru")
            
            # Wait for page to load
            time.sleep(5)
            
            # Accept cookies if present
            try:
                cookie_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
                cookie_button.click()
                logger.info("Accepted cookies")
            except:
                pass
            
            # Search for Coolie movie
            logger.info("Searching for Coolie movie...")
            
            # Method 1: Check if movie is in the listing
            page_source = self.driver.page_source.lower()
            
            if 'coolie' in page_source:
                logger.info("✅ Found Coolie movie!")
                
                # Try to click on the movie
                try:
                    # Find movie card/link
                    movie_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'coolie')]")
                    if movie_elements:
                        logger.info(f"Found {len(movie_elements)} Coolie movie links")
                        movie_elements[0].click()
                        time.sleep(3)
                        
                        # Check for Book Tickets button
                        try:
                            book_button = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Book tickets')]"))
                            )
                            logger.info("✅ Book tickets button found!")
                            book_button.click()
                            time.sleep(3)
                            
                            # Check for theaters
                            page_source = self.driver.page_source.lower()
                            
                            for screen in self.target_screens:
                                if screen.lower() in page_source:
                                    screens_found.append(screen)
                                    logger.info(f"🎯 Target screen available: {screen}")
                                    
                        except:
                            logger.info("Book tickets button not found yet")
                            
                except Exception as e:
                    logger.warning(f"Could not navigate to movie page: {e}")
                    
            else:
                logger.info("Coolie movie not found in listings")
                
                # Method 2: Direct URL approach
                logger.info("Trying direct movie URL...")
                self.driver.get("https://in.bookmyshow.com/bengaluru/movies/coolie-ET00395817")
                time.sleep(5)
                
                page_source = self.driver.page_source.lower()
                
                # Check for target screens in page source
                for screen in self.target_screens:
                    if screen.lower() in page_source:
                        screens_found.append(screen)
                        logger.info(f"🎯 Target screen mentioned: {screen}")
                        
        except Exception as e:
            logger.error(f"Error during Selenium check: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")
                
        return screens_found

    def send_alert(self, screens_found):
        """Send email alert"""
        if not self.email_config['email'] or not self.email_config['to_email']:
            logger.warning("Email configuration incomplete")
            return
        
        try:
            subject = f"🎬 Coolie - Target Screens Available!"
            
            body = f"""
🎬 COOLIE TICKET ALERT (Selenium Check) 🎬

Target screens detected:

"""
            for screen in screens_found:
                body += f"✅ {screen}\n"
            
            body += f"""

Visit BookMyShow NOW:
https://in.bookmyshow.com/bengaluru/movies/coolie-ET00395817

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Automated browser check successful!
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
        logger.info("🎬 COOLIE MONITOR (Selenium/Undetected Chrome)")
        logger.info("=" * 60)
        
        screens = self.check_availability()
        
        if screens:
            logger.info(f"✅ Found {len(screens)} target screens")
            self.send_alert(screens)
            return True
        else:
            logger.info("⏳ No target screens found")
            return False

def main():
    monitor = SeleniumBookMyShowMonitor()
    monitor.run()
    
    # Always exit with 0 for GitHub Actions
    import sys
    sys.exit(0)

if __name__ == "__main__":
    main()