#!/usr/bin/env python3
"""
District.in Coolie Ticket Monitor

Enhanced monitor for District.in with complete notification system.
Monitors District.in for Coolie movie ticket availability in Bengaluru PVR screens.
This module works alongside the BookMyShow monitor for comprehensive coverage.

Features:
- Session warming to avoid detection
- Smart screen matching for PVR locations
- Enhanced error handling
- Email notifications
- Voice call alerts via Twilio
- Booking URL extraction
- Rate limiting protection
"""

import requests
import random
import time
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DistrictMonitor:
    def __init__(self):
        """Initialize District.in monitor with configuration"""
        self.district_url = "https://www.district.in/movies/coolie-movie-tickets-in-bengaluru-MV172677?frmtid=ZcW3aqXSzc"
        
        # Get target screens from environment
        self.target_screens = [
            screen.strip() 
            for screen in os.getenv('TARGET_SCREENS', 'PVR Soul Spirit,PVR Centro Mall,PVR Nexus Koramangala').split(',')
            if screen.strip()
        ]
        
        # Email configuration
        self.email_config = {
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'email': os.getenv('EMAIL_USER'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'to_emails': [email.strip() for email in os.getenv('EMAIL_TO', '').split(',') if email.strip()]
        }
        
        # Twilio configuration for voice calls
        self.twilio_config = {
            'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
            'auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
            'studio_flow_sid': os.getenv('TWILIO_STUDIO_FLOW_SID'),
            'phone_number': os.getenv('TWILIO_PHONE_NUMBER'),
            'voice_call_to': [phone.strip() for phone in os.getenv('VOICE_CALL_TO', '').split(',') if phone.strip()],
            'enable_voice_calls': os.getenv('ENABLE_VOICE_CALLS', 'true').lower() == 'true'
        }
        
        # Setup session
        self.setup_session()
        
        logging.info(f"🎭 District.in Monitor initialized")
        logging.info(f"🎯 Target screens: {', '.join(self.target_screens)}")
        logging.info(f"📧 Email notifications: {len(self.email_config['to_emails'])} recipients")
        logging.info(f"📞 Voice calls: {len(self.twilio_config['voice_call_to'])} numbers ({'enabled' if self.twilio_config['enable_voice_calls'] else 'disabled'})")
    
    def setup_session(self):
        """Setup session with enhanced headers"""
        self.session = requests.Session()
        
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def session_warmup(self):
        """Warm up the session with preliminary requests to avoid detection"""
        try:
            logging.info("🔥 Warming up District.in session...")
            
            # Visit homepage first
            homepage_response = self.session.get(
                "https://www.district.in/",
                timeout=15,
                allow_redirects=True
            )
            
            if homepage_response.status_code == 200:
                logging.info("✅ Homepage visited successfully")
            
            # Add random delay
            time.sleep(random.uniform(1, 3))
            
            # Visit movies section
            movies_response = self.session.get(
                "https://www.district.in/movies",
                timeout=15,
                allow_redirects=True
            )
            
            if movies_response.status_code == 200:
                logging.info("✅ Movies page visited successfully")
            
            # Add another random delay
            time.sleep(random.uniform(1, 3))
            
            logging.info("🔥 Session warmed up successfully")
            return True
            
        except Exception as e:
            logging.error(f"❌ Session warmup failed: {str(e)}")
            return False

    def extract_district_screens(self, soup):
        """Extract cinema screens from District.in page with enhanced matching"""
        screens_found = []
        
        # Get all text content from the page
        page_text = soup.get_text().lower()
        
        # First, check if any target screens are mentioned in the page text
        for target_screen in self.target_screens:
            target_lower = target_screen.lower()
            target_parts = target_lower.split()
            
            # Check for exact match first
            if target_lower in page_text:
                screen_details = {
                    'name': target_screen,
                    'matched_target': target_screen,
                    'status': 'DETECTED_IN_TEXT',
                    'is_pvr': 'pvr' in target_lower
                }
                screens_found.append(screen_details)
                logging.info(f"✅ Found exact match in text: {target_screen}")
                continue
            
            # Check for partial matches (for PVR screens) - but be more strict
            if 'pvr' in target_lower:
                # For PVR screens, require "pvr" to be present along with the location name
                pvr_parts = [part for part in target_parts if part != 'pvr']
                
                # Check if ALL significant parts of the PVR name are present
                significant_parts = [part for part in pvr_parts if len(part) > 3]  # Skip small words
                if significant_parts:
                    # Require at least the main location name to be present WITH "pvr"
                    main_location = significant_parts[0]  # e.g., "centro", "soul", "nexus"
                    
                    # Check if "pvr" and the main location appear near each other
                    pvr_with_location = f"pvr {main_location}" in page_text or f"pvr{main_location}" in page_text
                    
                    if pvr_with_location:
                        screen_details = {
                            'name': target_screen,
                            'matched_target': target_screen,
                            'status': 'DETECTED_PARTIAL',
                            'is_pvr': True
                        }
                        screens_found.append(screen_details)
                        logging.info(f"✅ Found PVR partial match: {target_screen}")
                        continue
                    else:
                        # Don't count as found if PVR and location aren't together
                        logging.debug(f"❌ PVR {main_location} not found together on page")
            
            # Check for innovative multiplex specifically
            if 'innovative' in target_lower:
                if 'innovative' in page_text and 'multiplex' in page_text:
                    screen_details = {
                        'name': 'Innovative Multiplex',
                        'matched_target': target_screen,
                        'status': 'DETECTED_INNOVATIVE',
                        'is_pvr': False
                    }
                    screens_found.append(screen_details)
                    logging.info(f"✅ Found Innovative Multiplex in text")
                    continue
            
            # Disabled overly broad partial matching - causes too many false positives
            # Only exact matches and specific PVR/Innovative matches should count
            continue
        
        # Enhanced HTML element extraction as fallback
        cinema_selectors = [
            '.cinema-name', '.theater-name', '.venue-name', '.cinema', '.theater', '.venue',
            '[class*="cinema"]', '[class*="theater"]', '[class*="venue"]', '[class*="multiplex"]',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', '.card-title', '.listing-title', '.title',
            '.name', '.theater-info', '.venue-info', '.location-name', '.mall-name'
        ]
        
        for selector in cinema_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if 3 < len(text) < 100:  # Reasonable length for cinema names
                        text_lower = text.lower()
                        
                        # Check if this element text matches any target
                        for target_screen in self.target_screens:
                            target_lower = target_screen.lower()
                            target_parts = target_lower.split()
                            
                            # Skip if already found this target
                            if any(screen['matched_target'] == target_screen for screen in screens_found):
                                continue
                            
                            # Check for matches
                            if target_lower in text_lower:
                                screen_details = {
                                    'name': text,
                                    'matched_target': target_screen,
                                    'status': 'DETECTED_HTML',
                                    'is_pvr': 'pvr' in text_lower
                                }
                                screens_found.append(screen_details)
                                logging.info(f"✅ Found in HTML element: {text}")
                                break
                            
                            # PVR specific matching
                            elif 'pvr' in target_lower and 'pvr' in text_lower:
                                pvr_parts = [part for part in target_parts if part != 'pvr']
                                if any(part in text_lower for part in pvr_parts if len(part) > 2):
                                    screen_details = {
                                        'name': text,
                                        'matched_target': target_screen,
                                        'status': 'DETECTED_HTML_PVR',
                                        'is_pvr': True
                                    }
                                    screens_found.append(screen_details)
                                    logging.info(f"✅ Found PVR in HTML: {text}")
                                    break
                            
                            # Innovative multiplex specific
                            elif 'innovative' in target_lower and 'innovative' in text_lower:
                                screen_details = {
                                    'name': text,
                                    'matched_target': target_screen,
                                    'status': 'DETECTED_HTML_INNOVATIVE',
                                    'is_pvr': False
                                }
                                screens_found.append(screen_details)
                                logging.info(f"✅ Found Innovative in HTML: {text}")
                                break
            except Exception as e:
                logging.debug(f"Error processing selector {selector}: {e}")
                continue
        
        # Remove duplicates based on matched_target
        unique_screens = {}
        for screen in screens_found:
            target = screen['matched_target']
            if target not in unique_screens:
                unique_screens[target] = screen
        
        final_screens = list(unique_screens.values())
        
        if final_screens:
            logging.info(f"📍 Final screen detection results: {len(final_screens)} targets found")
            for screen in final_screens:
                logging.info(f"   🎯 {screen['matched_target']} -> {screen['name']} [{screen['status']}]")
        else:
            logging.info("❌ No target screens detected on District.in page")
        
        return final_screens
    
    def send_email_notification(self, screens_found, result_data):
        """Send email notification for bookable tickets only"""
        if not self.email_config['email'] or not self.email_config['to_emails']:
            logging.warning("📧 Email configuration incomplete - skipping email alert")
            return False
        
        try:
            # Only send email for actual bookable tickets
            has_tickets = result_data.get('tickets_found', False)
            if not has_tickets:
                logging.info("📧 No bookable tickets - skipping email notification")
                return False
                
            has_pvr_screens = any(screen.get('is_pvr', False) for screen in screens_found)
            
            # Set subject and urgency for bookable tickets
            if has_pvr_screens:
                subject = f"🎭🚨 DISTRICT.IN - PVR COOLIE TICKETS AVAILABLE! - {len(screens_found)} Screens!"
                urgency = "BOOK NOW - PVR LIVE ON DISTRICT.IN!"
            else:
                subject = f"🎭🚨 DISTRICT.IN - COOLIE TICKETS AVAILABLE! - {len(screens_found)} Screens!"
                urgency = "BOOK NOW ON DISTRICT.IN!"
            
            body = f"""
🎉 DISTRICT.IN COOLIE ALERT! 🎉

Platform: District.in
Status: {urgency}
Found: {len(screens_found)} of your preferred screens

TARGET SCREENS WITH BOOKABLE TICKETS:
"""
            
            for screen in screens_found:
                body += f"🎯 {screen['name']}\n"
                body += f"   Matched: {screen['matched_target']}\n"
                body += f"   Status: {screen['status']}\n"
                if screen.get('is_pvr'):
                    body += f"   Type: PVR Cinema ⭐\n"
                body += "\n"
            
            if result_data.get('showtimes'):
                body += f"⏰ Showtimes Available: {', '.join(result_data['showtimes'][:5])}\n\n"
            
            body += f"""
📱 DISTRICT.IN BOOKING URL: 
{self.district_url}

🔗 Quick Book Link: {self.district_url}

⏰ Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🏃‍♂️💨 URGENT: Tickets available on District.in! Book now!
👆 Click the link above or copy this URL: {self.district_url}

"""
            
            body += """
Your Target Screens (Bengaluru):
• PVR Soul Spirit
• PVR Centro Mall  
• PVR Nexus Koramangala
• Innovative Multiplex

Platform: District.in 🎭
Happy Booking! 🎬✨
"""
            
            # Send to all configured email addresses
            success_count = 0
            for to_email in self.email_config['to_emails']:
                try:
                    msg = MIMEMultipart()
                    msg['From'] = self.email_config['email']
                    msg['To'] = to_email
                    msg['Subject'] = subject
                    
                    msg.attach(MIMEText(body, 'plain'))
                    
                    server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
                    server.starttls()
                    server.login(self.email_config['email'], self.email_config['password'])
                    text = msg.as_string()
                    server.sendmail(self.email_config['email'], to_email, text)
                    server.quit()
                    
                    logging.info(f"📧 Email sent successfully to {to_email}")
                    success_count += 1
                    
                except Exception as e:
                    logging.error(f"❌ Failed to send email to {to_email}: {e}")
            
            if success_count > 0:
                logging.info(f"📧 Email notifications sent to {success_count}/{len(self.email_config['to_emails'])} recipients")
                return True
            return False
            
        except Exception as e:
            logging.error(f"❌ Email notification system error: {e}")
            return False
    
    def make_voice_calls(self, screens_found, result_data):
        """Make voice calls via Twilio for urgent notifications"""
        if not self.twilio_config['enable_voice_calls']:
            logging.info("📞 Voice calls disabled")
            return False
        
        if not all([
            self.twilio_config['account_sid'],
            self.twilio_config['auth_token'], 
            self.twilio_config['studio_flow_sid'],
            self.twilio_config['phone_number']
        ]):
            logging.warning("📞 Twilio configuration incomplete - skipping voice calls")
            return False
        
        if not self.twilio_config['voice_call_to']:
            logging.warning("📞 No voice call recipients configured")
            return False
        
        try:
            # Import Twilio here to avoid dependency issues if not configured
            from twilio.rest import Client
            
            client = Client(
                self.twilio_config['account_sid'], 
                self.twilio_config['auth_token']
            )
            
            has_tickets = result_data.get('tickets_found', False)
            has_pvr_screens = any(screen.get('is_pvr', False) for screen in screens_found)
            
            # Voice calls should only be made for actual bookable tickets with showtimes
            if not has_tickets:
                logging.info("📞 No bookable tickets found - skipping voice calls")
                return False
            
            success_count = 0
            for phone_number in self.twilio_config['voice_call_to']:
                try:
                    call = client.studio \
                        .flows(self.twilio_config['studio_flow_sid']) \
                        .executions \
                        .create(
                            to=phone_number,
                            from_=self.twilio_config['phone_number'],
                            parameters={
                                'platform': 'District.in',
                                'movie': 'Coolie',
                                'screens_count': str(len(screens_found)),
                                'has_pvr': 'yes' if has_pvr_screens else 'no',
                                'urgency': 'high' if has_tickets else 'medium'
                            }
                        )
                    
                    logging.info(f"📞 Voice call initiated to {phone_number}: {call.sid}")
                    success_count += 1
                    time.sleep(1)  # Small delay between calls
                    
                except Exception as e:
                    logging.error(f"❌ Failed to call {phone_number}: {e}")
            
            if success_count > 0:
                logging.info(f"📞 Voice calls initiated to {success_count}/{len(self.twilio_config['voice_call_to'])} numbers")
                return True
            return False
            
        except ImportError:
            logging.error("❌ Twilio library not installed. Install with: pip install twilio")
            return False
        except Exception as e:
            logging.error(f"❌ Voice call system error: {e}")
            return False
    
    def check_district_availability(self):
        """
        Check District.in for Coolie ticket availability with enhanced notification system
        
        Returns:
            Dict with screening results and notification status
        """
        try:
            # Warm up session first
            if not self.session_warmup():
                return {
                    'success': False,
                    'tickets_found': False,
                    'screens_found': [],
                    'message': 'Session warmup failed',
                    'notifications_sent': False
                }
            
            logging.info(f"🎭 Checking District.in for Coolie tickets: {self.district_url}")
            
            # Add random delay before main request
            time.sleep(random.uniform(2, 5))
            
            # Make the main request
            response = self.session.get(self.district_url, timeout=20, allow_redirects=True)
            
            logging.info(f"📊 District.in Response Status: {response.status_code}")
            
            if response.status_code == 403:
                logging.warning("🚫 District.in returned 403 Forbidden - Rate limited")
                return {
                    'success': False,
                    'tickets_found': False,
                    'screens_found': [],
                    'message': '403 Forbidden - Rate limited',
                    'notifications_sent': False
                }
            
            if response.status_code != 200:
                logging.error(f"❌ District.in HTTP Error: {response.status_code}")
                return {
                    'success': False,
                    'tickets_found': False,
                    'screens_found': [],
                    'message': f'HTTP {response.status_code}',
                    'notifications_sent': False
                }
            
            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract screens using the dedicated function
            screens_found = self.extract_district_screens(soup)
            
            # Check for Coolie-specific context
            # Get page text and add spaces where needed (times often concatenated with SCREEN labels)
            import re
            raw_text = soup.get_text()
            # Add spaces between times and SCREEN labels
            page_text = re.sub(r'(\d{2}:\d{2}\s*[AP]M)([A-Z])', r'\1 \2', raw_text, flags=re.IGNORECASE)
            # Add spaces between lowercase and uppercase transitions
            page_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', page_text)
            page_text = page_text.lower()
            coolie_context_found = 'coolie' in page_text
            
            # Look for screen-specific indicators (like SCREEN2, SCREEN4, etc.)
            screen_indicators = ['screen1', 'screen2', 'screen3', 'screen4', 'screen5', 
                               'screen 1', 'screen 2', 'screen 3', 'screen 4', 'screen 5']
            has_screen_indicators = any(indicator in page_text for indicator in screen_indicators)
            
            # Enhanced validation - look for booking indicators
            strong_booking_indicators = [
                'select seats', 'book now', 'buy now', 'choose seats',
                'select show', 'book your seats'
            ]
            
            # Check for weak booking indicators separately
            weak_booking_indicators = [
                'book tickets', 'buy tickets', 'available', 'choose time'
            ]
            
            has_strong_booking = any(indicator in page_text for indicator in strong_booking_indicators)
            has_weak_booking = any(indicator in page_text for indicator in weak_booking_indicators)
            
            # For actual booking, we accept strong indicators OR screen indicators with times
            tickets_available = has_strong_booking or has_screen_indicators
            
            # Look for showtimes
            showtimes = []
            coolie_showtimes_confirmed = False
            
            import re
            # More flexible time pattern that catches various formats
            # Matches: "06:45 AM", "06:45AM", "06:45 am", "12:45 PM", "12:45 pm"
            time_pattern = re.compile(r'(\d{1,2}:\d{2}\s*(?:am|pm))', re.IGNORECASE)
            
            # First, try to find showtimes near screen names
            if screens_found:
                for screen in screens_found:
                    # Try multiple variations of the screen name
                    screen_variations = [
                        screen['name'].lower(),
                        screen['matched_target'].lower(),
                        'innovative',  # Specifically for Innovative Multiplex
                        'multiplex'
                    ]
                    
                    for variation in screen_variations:
                        if variation in page_text:
                            # Find the position of this variation in the page
                            screen_pos = page_text.find(variation)
                            if screen_pos != -1:
                                # Extract a larger context around the screen
                                context_start = max(0, screen_pos - 200)
                                context_end = min(len(page_text), screen_pos + 1500)
                                context = page_text[context_start:context_end]
                                
                                # Look for times in this context
                                found_times = time_pattern.findall(context)
                                if found_times:
                                    showtimes.extend(found_times[:10])  # Get up to 10 times
                                    # If we found times near the screen AND Coolie is on the page, confirm
                                    if coolie_context_found:
                                        coolie_showtimes_confirmed = True
                                        logging.info(f"✅ Found showtimes near {screen['name']}: {found_times[:5]}")
                                    break  # Stop checking variations once we found times
            
            # If no showtimes found near screens, look more broadly
            if not showtimes:
                # Look for any cluster of times (indicating a showtime schedule)
                all_times = time_pattern.findall(page_text)
                
                # If we find multiple times and the page has our target screen and Coolie context
                if len(all_times) >= 3 and screens_found and coolie_context_found:
                    # Check if times appear in clusters (typical of movie showtimes)
                    # Find positions of all times
                    time_positions = []
                    for time_str in all_times[:20]:  # Check first 20 times
                        pos = page_text.find(time_str.lower())
                        if pos != -1:
                            time_positions.append((pos, time_str))
                    
                    # Sort by position
                    time_positions.sort(key=lambda x: x[0])
                    
                    # Look for clusters of times (multiple times within 200 chars)
                    clustered_times = []
                    for i, (pos, time_str) in enumerate(time_positions):
                        # Check if next time is within 200 chars
                        if i < len(time_positions) - 1:
                            next_pos = time_positions[i + 1][0]
                            if next_pos - pos < 200:  # Times are close together
                                clustered_times.append(time_str)
                    
                    if clustered_times:
                        showtimes = clustered_times[:10]
                        coolie_showtimes_confirmed = True
                        logging.info(f"✅ Found clustered showtimes on page: {showtimes[:5]}")
            
            # Remove duplicates and validate times
            validated_showtimes = []
            for time_str in set(showtimes):
                # Basic validation - check if it looks like a real time
                try:
                    time_parts = re.findall(r'\d+', time_str)
                    if time_parts and len(time_parts) >= 2:
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])
                        # Validate hour and minute ranges
                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                            validated_showtimes.append(time_str)
                        elif 1 <= hour <= 12 and 0 <= minute <= 59:  # 12-hour format
                            validated_showtimes.append(time_str)
                except:
                    continue
            
            showtimes = validated_showtimes[:10]  # Limit to 10 showtimes
            
            # BALANCED validation: Avoid false positives while detecting real bookings
            # We need target screens + Coolie context + (showtimes OR booking indicators)
            has_bookable_tickets = (
                len(screens_found) > 0 and              # Target screens found
                coolie_context_found and                # Coolie movie mentioned on page
                (
                    # Either we have confirmed showtimes
                    (len(showtimes) > 0 and coolie_showtimes_confirmed) or
                    # Or we have strong booking indicators with screen indicators
                    (tickets_available and has_screen_indicators) or
                    # Or we have strong booking with validated times
                    (has_strong_booking and len(validated_showtimes) > 0)
                )
            )
            
            # Log validation details for debugging
            logging.info(f"📊 Validation Results:")
            logging.info(f"   - Screens found: {len(screens_found)}")
            logging.info(f"   - Coolie context: {coolie_context_found}")
            logging.info(f"   - Strong booking indicators: {has_strong_booking}")
            logging.info(f"   - Weak booking indicators: {has_weak_booking}")
            logging.info(f"   - Coolie showtimes confirmed: {coolie_showtimes_confirmed}")
            logging.info(f"   - Valid showtimes: {len(showtimes)}")
            logging.info(f"   - Has bookable tickets: {has_bookable_tickets}")
            
            result = {
                'success': True,
                'tickets_found': has_bookable_tickets,
                'screens_found': screens_found,
                'message': f"Found {len(screens_found)} matching screens",
                'booking_url': self.district_url,
                'showtimes': showtimes if showtimes else [],
                'notifications_sent': False
            }
            
            # Send notifications ONLY when actual booking is available (screens + showtimes + booking indicators)
            if has_bookable_tickets:
                notifications_sent = False
                
                # Send email notifications for actual bookable tickets
                email_sent = self.send_email_notification(screens_found, result)
                
                # Make voice calls for urgent bookable tickets
                voice_sent = self.make_voice_calls(screens_found, result)
                
                notifications_sent = email_sent or voice_sent
                result['notifications_sent'] = notifications_sent
                
                logging.info(f"🎉 District.in SUCCESS! Found BOOKABLE tickets at {len(screens_found)} target screens with {len(showtimes)} showtimes!")
                logging.info(f"📢 Notifications sent: Email={email_sent}, Voice={voice_sent}")
                
            elif screens_found:
                # Screens found but no booking available yet - just log, no notifications
                logging.info(f"👀 District.in: Target screens detected ({len(screens_found)}) but booking not yet open")
                if tickets_available:
                    logging.info(f"⏰ Booking indicators found but no showtimes available yet")
                else:
                    logging.info(f"⏳ No booking indicators found yet")
                    
            else:
                logging.info(f"⏳ District.in: No target screens found yet.")
            
            return result
            
        except requests.RequestException as e:
            logging.error(f"❌ District.in request failed: {str(e)}")
            return {
                'success': False,
                'tickets_found': False,
                'screens_found': [],
                'message': f'Request failed: {str(e)}',
                'notifications_sent': False
            }
        
        except Exception as e:
            logging.error(f"❌ District.in unexpected error: {str(e)}")
            return {
                'success': False,
                'tickets_found': False,
                'screens_found': [],
                'message': f'Unexpected error: {str(e)}',
                'notifications_sent': False
            }
    
    def run_once(self):
        """Run a single check"""
        logging.info("=" * 60)
        logging.info("🎭 DISTRICT.IN MONITOR - SINGLE CHECK")
        logging.info("=" * 60)
        
        result = self.check_district_availability()
        
        if result['tickets_found']:
            logging.info("🎉 SUCCESS! Tickets found on District.in!")
            return True
        elif result['screens_found']:
            logging.info("👀 Target screens detected - continuing to monitor...")
            return False
        else:
            logging.info("⏳ No target screens found yet")
            return False
    
    def run_continuous(self, check_interval_minutes=5):
        """Run continuous monitoring"""
        logging.info("=" * 60)
        logging.info("🎭 DISTRICT.IN MONITOR - CONTINUOUS MODE")
        logging.info(f"Checking every {check_interval_minutes} minutes")
        logging.info(f"Target screens: {', '.join(self.target_screens)}")
        logging.info("=" * 60)
        
        while True:
            try:
                result = self.check_district_availability()
                
                if result['tickets_found']:
                    logging.info("🎉 SUCCESS! Tickets found on District.in - continuing to monitor for more!")
                    # Don't break - keep monitoring for other screens or showtimes
                
                # Wait before next check
                logging.info(f"💤 Waiting {check_interval_minutes} minutes before next check...")
                time.sleep(check_interval_minutes * 60)
                
            except KeyboardInterrupt:
                logging.info("🛑 District.in monitor stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ District.in monitor error: {e}")
                logging.info(f"💤 Waiting 60 seconds before retry...")
                time.sleep(60)

# Legacy function for backward compatibility
def check_district_availability(target_screens):
    """Legacy function - creates monitor instance and runs check"""
    monitor = DistrictMonitor()
    result = monitor.check_district_availability()
    return {
        'success': result['success'],
        'tickets_found': result['tickets_found'],
        'screens_found': [f"{screen['name']} (matches {screen['matched_target']})" for screen in result['screens_found']],
        'message': result['message'],
        'booking_url': result.get('booking_url', monitor.district_url),
        'showtimes': result.get('showtimes', [])
    }

def main():
    """Main function for District.in monitoring"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🎭 Starting Enhanced District.in Monitor")
    print("🔧 Loading configuration...")
    
    try:
        # Create monitor instance
        monitor = DistrictMonitor()
        
        print("✅ Configuration loaded successfully!")
        print(f"🎯 Target screens: {', '.join(monitor.target_screens)}")
        print(f"📧 Email recipients: {len(monitor.email_config['to_emails'])}")
        print(f"📞 Voice call recipients: {len(monitor.twilio_config['voice_call_to'])}")
        print("=" * 60)
        
        # Run continuous monitoring
        monitor.run_continuous(check_interval_minutes=5)
        
    except KeyboardInterrupt:
        print("\n🛑 District.in monitor stopped by user")
    except Exception as e:
        logging.error(f"❌ District.in monitor startup error: {e}")

if __name__ == "__main__":
    main()
