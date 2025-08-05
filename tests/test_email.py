#!/usr/bin/env python3

"""Direct email test to verify SMTP configuration"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_email():
    # Load credentials from environment
    from_email = os.getenv('EMAIL_FROM', '').strip('"')
    to_email = os.getenv('EMAIL_TO', '').strip('"')
    password = os.getenv('EMAIL_PASSWORD', '').strip('"')
    
    print(f"Testing email configuration...")
    print(f"From: {from_email}")
    print(f"To: {to_email}")
    print(f"Password length: {len(password)}")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = "🎬 Test Alert - Email System Working!"
        
        body = f"""
This is a test email from your Coolie Ticket Alert System.

✅ Email configuration is working correctly!

Test details:
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- From: {from_email}
- To: {to_email}

Your ticket alert system is ready to notify you when Coolie tickets become available.

---
Automated ticket alert system test
        """.strip()
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print("\nConnecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("Authenticating...")
        server.login(from_email, password)
        
        print("Sending email...")
        server.send_message(msg)
        server.quit()
        
        print("\n✅ SUCCESS! Test email sent successfully!")
        print(f"Check your inbox at {to_email}")
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ Authentication failed!")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're using an App Password (not your regular Gmail password)")
        print("2. Enable 2-Factor Authentication in your Google Account")
        print("3. Generate App Password at: https://myaccount.google.com/apppasswords")
        print("4. Use the 16-character password without spaces")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_email()