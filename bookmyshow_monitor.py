#!/usr/bin/env python3
"""
BookMyShow Ticket Monitor for Specific Screens
Monitors ticket availability for Coolie movie in preferred PVR screens in Bengaluru
"""

import requests
import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

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

class BookMyShowMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://in.bookmyshow.com/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'max-age=0'
        })
        
        # Target screens - your preferred PVR locations
        self.target_screens = [
            "PVR Soul Spirit",
            "PVR Centro Mall", 
            "PVR Nexus Koramangala",
            "PNR felicity mall"  # Note: keeping as you specified, might be "PVR Felicity Mall"
        ]
        
        # BookMyShow URL for Coolie tickets (14th August 2025)
        self.booking_url = "https://in.bookmyshow.com/movies/bengaluru/coolie/buytickets/ET00395817/20250814"
        
        # Email configuration
        self.email_config = {
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'email': os.getenv('EMAIL_USER'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'to_email': os.getenv('EMAIL_TO')
        }

    def check_screen_availability(self):
        """Check if tickets are available in target screens"""
        try:
            logger.info("🎬 Checking BookMyShow for Coolie tickets...")
            logger.info(f"URL: {self.booking_url}")
            logger.info(f"Target screens: {', '.join(self.target_screens)}")
            
            response = self.session.get(self.booking_url, timeout=30)
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Failed to access booking page: {response.status_code}")
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Log page title for verification
            title = soup.find('title')
            if title:
                logger.info(f"Page title: {title.get_text().strip()}")
            
            # Find all cinemas/screens on the page
            available_screens = self.extract_available_screens(soup)
            
            # Check which target screens have availability or are ready for booking
            matching_screens = {}
            target_screens_found = 0
            booking_status = "WAITING"
            
            for screen_name, details in available_screens.items():
                # Check if this is a target screen
                is_target = '🎯' in screen_name or any(target.lower() in screen_name.lower() for target in self.target_screens)
                
                if is_target:
                    target_screens_found += 1
                    status = details.get('status', 'UNKNOWN')
                    
                    if status in ['BOOKING_OPEN', 'BOOKING_OPENING']:
                        matching_screens[screen_name] = details
                        booking_status = "READY"
                        logger.info(f"✅ TARGET SCREEN READY: {screen_name} (Status: {status})")
                    else:
                        logger.info(f"🎯 Target screen found but not ready: {screen_name} (Status: {status})")
                
                # Also check non-target screens with actual showtimes
                elif details.get('status') == 'BOOKING_OPEN' and details.get('showtimes'):
                    logger.info(f"📍 Other cinema with active booking: {screen_name}")
            
            logger.info(f"📊 Summary: {target_screens_found} target screens found, {len(matching_screens)} ready for booking")
            
            if matching_screens:
                logger.info(f"� Found {len(matching_screens)} target screens ready for booking!")
                return matching_screens
            elif target_screens_found > 0:
                logger.info(f"🎯 Found {target_screens_found} target screens but booking not yet open")
                logger.info("Available target screens:")
                for screen in available_screens.keys():
                    if '🎯' in screen:
                        status = available_screens[screen].get('status', 'UNKNOWN')
                        logger.info(f"  - {screen} ({status})")
                return {}
            else:
                logger.info("❌ No target screens found")
                logger.info("Available screens found:")
                for screen in list(available_screens.keys())[:5]:  # Show first 5
                    logger.info(f"  - {screen}")
                return {}
                
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return {}

    def extract_available_screens(self, soup):
        """Extract available screens and detect when booking opens"""
        available_screens = {}
        page_text = soup.get_text()
        all_text_lower = page_text.lower()
        
        logger.info("🔍 Checking for cinema availability and booking status...")
        
        # Strategy 1: Look for actual cinema names with showtimes 
        lines = page_text.split('\n')
        active_cinemas = []
        
        import re
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) > 300:
                continue
                
            line_lower = line.lower()
            
            # Check if this line contains a cinema name
            if any(keyword in line_lower for keyword in ['cinema', 'cinemas', 'theatre', 'theater', 'multiplex']):
                # Look for time patterns in nearby lines
                context_lines = lines[max(0, i-2):min(len(lines), i+3)]
                context_text = ' '.join(context_lines)
                
                time_patterns = re.findall(r'\b\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)\b', context_text)
                if time_patterns:
                    available_screens[line] = {
                        'showtimes': time_patterns,
                        'source': 'active_showtimes',
                        'status': 'BOOKING_OPEN'
                    }
                    active_cinemas.append(line)
                    logger.info(f"✅ ACTIVE CINEMA: {line}")
        
        # Strategy 2: Check if BookMyShow page shows general booking availability
        booking_indicators = ['book tickets', 'buy tickets', 'select seats', 'showtimes', 'book now']
        general_booking_available = any(indicator in all_text_lower for indicator in booking_indicators)
        
        # Count time patterns in the page
        all_times = re.findall(r'\b\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)\b', page_text)
        has_showtimes = len(all_times) > 5  # More than 5 time patterns suggests active booking
        
        # Strategy 3: Always monitor for target screens (even if not active yet)
        target_screens_on_page = []
        
        # Check for Soul Spirit
        if any(term in all_text_lower for term in ['soul spirit', 'soulspirit']):
            target_screens_on_page.append("PVR Soul Spirit Central Mall, Bellandur")
        
        # Check for Centro Mall  
        if 'centro' in all_text_lower:
            target_screens_on_page.append("PVR Centro Mall")
        
        # Check for Nexus Koramangala
        if 'nexus' in all_text_lower and 'koramangala' in all_text_lower:
            target_screens_on_page.append("PVR Nexus Koramangala")
        
        # Check for Felicity
        if 'felicity' in all_text_lower:
            target_screens_on_page.append("PVR Felicity Mall")
        
        # Determine overall booking status
        if len(active_cinemas) > 0:
            booking_status = "SOME_CINEMAS_OPEN"
            logger.info(f"🎬 Booking appears to be ACTIVE - {len(active_cinemas)} cinemas showing Coolie")
        elif has_showtimes and general_booking_available:
            booking_status = "BOOKING_OPENING"
            logger.info("🕐 Booking infrastructure detected - may be opening soon")
        else:
            booking_status = "NOT_OPEN_YET"
            logger.info("⏳ Booking not yet open - no active showtimes found")
        
        # Add target screens with appropriate status
        for target in target_screens_on_page:
            # Check if this target screen has actual showtimes
            target_has_showtimes = any(target.lower() in cinema.lower() for cinema in active_cinemas)
            
            if target_has_showtimes:
                status = "BOOKING_OPEN"
                note = "🎉 TARGET SCREEN IS LIVE! Book now!"
            elif booking_status == "SOME_CINEMAS_OPEN":
                status = "BOOKING_OPENING" 
                note = "Booking is opening - target screen should be available soon!"
            else:
                status = "WAITING"
                note = "Target screen detected but booking not yet open"
            
            available_screens[f"🎯 {target}"] = {
                'showtimes': [],
                'source': 'target_monitoring',
                'status': status,
                'note': note
            }
            logger.info(f"🎯 TARGET MONITORED: {target} (Status: {status})")
        
        # Log summary
        logger.info(f"📊 Booking Status: {booking_status}")
        logger.info(f"📊 Active cinemas: {len(active_cinemas)}")
        logger.info(f"📊 Target screens found: {len(target_screens_on_page)}")
        logger.info(f"📊 Time patterns detected: {len(all_times)}")
        
        return available_screens

    def find_showtimes_in_context(self, cinema_line, all_lines, line_index):
        """Find showtimes near a cinema name in the text"""
        showtimes = []
        
        # Look in the cinema line itself and nearby lines
        search_lines = [cinema_line]
        
        # Add lines before and after
        for offset in range(-3, 4):
            try:
                if 0 <= line_index + offset < len(all_lines):
                    search_lines.append(all_lines[line_index + offset])
            except:
                pass
        
        import re
        # Look for time patterns
        for line in search_lines:
            time_patterns = re.findall(r'\b\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)\b', line)
            showtimes.extend(time_patterns)
        
        return list(set(showtimes))  # Remove duplicates

    def send_alert(self, matching_screens):
        """Send email alert for available screens"""
        if not self.email_config['email'] or not self.email_config['to_email']:
            logger.warning("Email configuration incomplete - skipping email alert")
            return
        
        try:
            # Determine alert type
            has_open_booking = any(details.get('status') == 'BOOKING_OPEN' for details in matching_screens.values())
            has_opening_booking = any(details.get('status') == 'BOOKING_OPENING' for details in matching_screens.values())
            
            if has_open_booking:
                subject = f"🎬🚨 COOLIE BOOKING OPEN! - {len(matching_screens)} Target Screens Ready!"
                urgency = "BOOK NOW!"
            elif has_opening_booking:
                subject = f"🎬⏰ COOLIE Booking Opening Soon - {len(matching_screens)} Target Screens Detected!"
                urgency = "Be Ready!"
            else:
                subject = f"🎬📍 COOLIE Target Screens Found - {len(matching_screens)} Locations"
                urgency = "Monitor Active"
            
            body = f"""
🎉 COOLIE TICKET ALERT! 🎉

Status: {urgency}
Found: {len(matching_screens)} of your preferred screens

TARGET SCREENS:
"""
            
            for screen_name, details in matching_screens.items():
                status = details.get('status', 'UNKNOWN')
                body += f"🎯 {screen_name.replace('🎯 ', '')}\n"
                body += f"   Status: {status}\n"
                
                if details.get('showtimes'):
                    body += f"   Show times: {', '.join(details['showtimes'][:5])}\n"
                
                if details.get('note'):
                    body += f"   Note: {details['note']}\n"
                
                body += "\n"
            
            body += f"""
📱 BOOKING URL: {self.booking_url}

⏰ Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
            
            if has_open_booking:
                body += "🏃‍♂️💨 URGENT: Booking is OPEN! Book your tickets now!\n"
            elif has_opening_booking:
                body += "⏰ Booking appears to be opening soon. Stay ready!\n"
            else:
                body += "👀 Keep monitoring - target screens detected!\n"
            
            body += """
Your Preferred Screens:
• PVR Soul Spirit
• PVR Centro Mall  
• PVR Nexus Koramangala
• PVR Felicity Mall

Happy Booking! �✨
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
        logger.info("🎬 COOLIE TICKET MONITOR - SINGLE CHECK")
        logger.info("=" * 60)
        
        matching_screens = self.check_screen_availability()
        
        if matching_screens:
            logger.info("🎉 SUCCESS! Target screens found with availability!")
            self.send_alert(matching_screens)
            return True
        else:
            logger.info("⏳ No target screens available yet")
            return False

    def run_continuous(self, check_interval_minutes=5):
        """Run continuous monitoring"""
        logger.info("=" * 60)
        logger.info("🎬 COOLIE TICKET MONITOR - CONTINUOUS MODE")
        logger.info(f"Checking every {check_interval_minutes} minutes")
        logger.info(f"Target screens: {', '.join(self.target_screens)}")
        logger.info("=" * 60)
        
        while True:
            try:
                matching_screens = self.check_screen_availability()
                
                if matching_screens:
                    logger.info("🎉 SUCCESS! Target screens found - sending alert and stopping!")
                    self.send_alert(matching_screens)
                    break
                else:
                    logger.info(f"⏳ No target screens available. Sleeping for {check_interval_minutes} minutes...")
                    time.sleep(check_interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                logger.info("Sleeping for 1 minute before retry...")
                time.sleep(60)

def main():
    """Main function"""
    import sys
    
    monitor = BookMyShowMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--once":
            success = monitor.run_once()
            # Exit with code 0 if tickets found, 1 if not (useful for GitHub Actions)
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--continuous":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            monitor.run_continuous(interval)
        else:
            print("Usage: python bookmyshow_monitor.py [--once|--continuous [interval_minutes]]")
            sys.exit(1)
    else:
        # Default to single check for GitHub Actions
        success = monitor.run_once()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
