#!/usr/bin/env python3
"""
Simplified checker for GitHub Actions that focuses on working platforms
"""

import os
import sys
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def check_district_paytm():
    """Check District/Paytm which works from GitHub Actions"""
    url = "https://paytm.com/movies/coolie-movie-detail-172677"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        
        # Check if booking is available
        text = response.text.lower()
        if any(keyword in text for keyword in ['book ticket', 'buy ticket', 'book now']):
            if 'notify me' not in text and 'coming soon' not in text:
                return True, response.url
    except Exception as e:
        print(f"Error checking District: {e}")
    
    return False, None

def send_alert(platform, url):
    """Send email alert"""
    from_email = os.getenv('EMAIL_FROM')
    to_email = os.getenv('EMAIL_TO')
    password = os.getenv('EMAIL_PASSWORD')
    
    if not all([from_email, to_email, password]):
        print("❌ Email credentials not configured!")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = f"🎬 Coolie Tickets Available on {platform}!"
    
    body = f"""
🎉 Tickets for Coolie (Tamil) are now available!

Platform: {platform}
URL: {url}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Book now before they sell out!
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Alert sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def main():
    print("🎬 Checking Coolie ticket availability...")
    print(f"Time: {datetime.now()}")
    
    # Check if already alerted
    state_file = "github_state.txt"
    if os.path.exists(state_file):
        print("Already alerted previously. Exiting.")
        return
    
    # Check District/Paytm
    available, url = check_district_paytm()
    
    if available:
        print("🎉 TICKETS AVAILABLE!")
        if send_alert("District/Paytm", url):
            # Mark as alerted
            with open(state_file, 'w') as f:
                f.write(f"Alerted at {datetime.now()}")
    else:
        print("No tickets available yet.")

if __name__ == "__main__":
    main()