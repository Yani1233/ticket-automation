#!/usr/bin/env python3

"""Integration tests for ticket alert system"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ticket_alert import TicketAlert

if __name__ == "__main__":
    print("🎬 Testing Email Alert System with Currently Showing Movies")
    print("=" * 60)
    
    # Use test configuration
    alert_system = TicketAlert(config_path='configs/test_movies.yaml')
    
    # Override state file to force alerts
    alert_system.state_file = 'test_state.json'
    
    # Run check once
    print("\n📧 Email credentials loaded from .env file")
    print(f"From: {os.getenv('EMAIL_FROM', 'Not set')}")
    print(f"To: {os.getenv('EMAIL_TO', 'Not set')}")
    print(f"Password: {'*' * len(os.getenv('EMAIL_PASSWORD', '')) if os.getenv('EMAIL_PASSWORD') else 'Not set'}")
    
    print("\n🔍 Checking for currently showing movies...")
    alert_system.run_check()
    
    print("\n✅ Test complete! Check your email and test_alert.log for results.")