#!/usr/bin/env python3
"""
Continuous Monitor for Coolie Tickets
Alternative to main.py - runs monitors sequentially instead of in threads
"""

import os
import sys
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import monitors
from bookmyshow_monitor import BookMyShowMonitor
from district_monitor import DistrictMonitor

def setup_logging():
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    log_filename = f'logs/continuous_{datetime.now().strftime("%Y%m%d")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

def display_header():
    """Display header information"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("="*70)
    print("🎬 COOLIE TICKET MONITOR - CONTINUOUS MODE")
    print("="*70)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Targets: {os.getenv('TARGET_SCREENS', 'Not configured')}")
    print(f"⏰ Interval: Every {os.getenv('CHECK_INTERVAL_MINUTES', '5')} minutes")
    print("="*70)
    print("\n💡 Press Ctrl+C to stop monitoring\n")
    print("-"*70)

def run_single_check():
    """Run a single check on both platforms"""
    check_time = datetime.now().strftime('%H:%M:%S')
    print(f"\n[{check_time}] 🔍 Starting check...")
    
    tickets_found = False
    
    try:
        # Check BookMyShow
        print(f"[{check_time}] 📱 Checking BookMyShow...")
        bms_monitor = BookMyShowMonitor()
        bms_screens = bms_monitor.check_screen_availability()
        
        if bms_screens:
            print(f"[{check_time}] 🎉 BookMyShow: {len(bms_screens)} screens ready!")
            for screen, details in bms_screens.items():
                print(f"                 ✅ {screen}: {details.get('status', 'Available')}")
            bms_monitor.send_alert(bms_screens)
            tickets_found = True
        else:
            print(f"[{check_time}] ⏳ BookMyShow: No tickets yet")
    
    except Exception as e:
        print(f"[{check_time}] ❌ BookMyShow error: {e}")
        logging.error(f"BookMyShow error: {e}")
    
    # Small delay between checks
    time.sleep(2)
    
    try:
        # Check District.in
        print(f"[{check_time}] 🎭 Checking District.in...")
        district_monitor = DistrictMonitor()
        district_result = district_monitor.check_district_availability()
        
        if district_result['tickets_found']:
            print(f"[{check_time}] 🎉 District.in: {len(district_result['screens_found'])} screens ready!")
            for screen in district_result['screens_found']:
                print(f"                 ✅ {screen['name']}")
            tickets_found = True
        else:
            print(f"[{check_time}] ⏳ District.in: No tickets yet")
    
    except Exception as e:
        print(f"[{check_time}] ❌ District.in error: {e}")
        logging.error(f"District.in error: {e}")
    
    return tickets_found

def main():
    """Main execution loop"""
    # Check for .env file
    if not os.path.exists('.env'):
        print("❌ ERROR: .env file not found!")
        print("Please copy .env.template to .env and configure your settings.")
        sys.exit(1)
    
    # Setup
    setup_logging()
    display_header()
    
    # Get check interval
    check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', '5'))
    check_count = 0
    
    # Main monitoring loop
    while True:
        try:
            check_count += 1
            print(f"\n{'='*70}")
            print(f"📊 Check #{check_count}")
            print('='*70)
            
            # Run the check
            tickets_found = run_single_check()
            
            if tickets_found:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🎊 TICKETS FOUND! Check your email/phone!")
                # Continue monitoring even after finding tickets
            
            # Display next check time
            next_check = datetime.now().timestamp() + (check_interval * 60)
            next_check_time = datetime.fromtimestamp(next_check).strftime('%H:%M:%S')
            print(f"\n💤 Next check at {next_check_time} (in {check_interval} minutes)")
            print("-"*70)
            
            # Sleep until next check
            time.sleep(check_interval * 60)
            
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("🛑 MONITORING STOPPED")
            print("="*70)
            print(f"📊 Total checks performed: {check_count}")
            print(f"🕐 Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*70)
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            logging.error(f"Main loop error: {e}")
            print("⏳ Retrying in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()