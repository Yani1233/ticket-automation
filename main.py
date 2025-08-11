#!/usr/bin/env python3
"""
Coolie Ticket Monitor - Main Runner

Monitors both BookMyShow and District.in for Coolie movie tickets.
Automatically sends email and voice call notifications when tickets become available.
"""

import os
import sys
import time
import threading
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the monitors
import bookmyshow_monitor
import district_monitor

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Generate log filename with date
    log_filename = f'logs/monitor_{datetime.now().strftime("%Y%m%d")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

def run_bookmyshow_monitor():
    """Run BookMyShow monitor in a separate thread"""
    try:
        logging.info("🎬 Starting BookMyShow monitor...")
        # Create monitor instance and run continuously
        monitor = bookmyshow_monitor.BookMyShowMonitor()
        monitor.run_continuous(check_interval_minutes=5)  # Check every 5 minutes
    except Exception as e:
        logging.error(f"❌ BookMyShow monitor error: {e}")

def run_district_monitor():
    """Run District.in monitor in a separate thread"""
    try:
        logging.info("🏛️ Starting District.in monitor...")
        # Create monitor instance and run continuously
        monitor = district_monitor.DistrictMonitor()
        monitor.run_continuous(check_interval_minutes=5)  # Check every 5 minutes
    except Exception as e:
        logging.error(f"❌ District.in monitor error: {e}")

def display_status():
    """Display current monitoring status"""
    target_screens = os.getenv('TARGET_SCREENS', 'Not configured').split(',')
    email_recipients = os.getenv('EMAIL_TO', 'Not configured').split(',')
    voice_recipients = os.getenv('VOICE_CALL_TO', 'Not configured').split(',')
    voice_enabled = os.getenv('ENABLE_VOICE_CALLS', 'false').lower() == 'true'
    
    print("\n" + "="*70)
    print("🎬 COOLIE TICKET MONITOR - CONFIGURATION")
    print("="*70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n🎯 TARGET SCREENS ({len(target_screens)}):")
    for screen in target_screens:
        print(f"   • {screen.strip()}")
    print(f"\n📧 EMAIL RECIPIENTS ({len(email_recipients)}):")
    for email in email_recipients:
        print(f"   • {email.strip()}")
    print(f"\n📞 VOICE CALLS: {'Enabled' if voice_enabled else 'Disabled'}")
    if voice_enabled:
        print(f"   Recipients ({len(voice_recipients)}):")
        for phone in voice_recipients:
            print(f"   • {phone.strip()}")
    print(f"\n⏰ Check Interval: Every {os.getenv('CHECK_INTERVAL_MINUTES', '5')} minutes")
    print("="*70 + "\n")

def main():
    """Main execution - runs both monitors"""
    # Clear screen for better visibility
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("="*70)
    print("🚀 COOLIE TICKET AUTOMATION SYSTEM")
    print("="*70)
    print("📱 Platforms: BookMyShow + District.in")
    print("🎬 Movie: Coolie (Tamil)")
    print("📍 Location: Bengaluru")
    print("="*70)
    
    setup_logging()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n❌ ERROR: .env file not found!")
        print("Please copy .env.template to .env and configure your settings.")
        return
    
    # Display current configuration
    display_status()
    
    try:
        # Create threads for both monitors
        bookmyshow_thread = threading.Thread(target=run_bookmyshow_monitor, name="BookMyShow")
        district_thread = threading.Thread(target=run_district_monitor, name="District.in")
        
        # Start both monitors
        print("\n🔄 Starting monitors...")
        bookmyshow_thread.start()
        time.sleep(2)  # Small delay between starts
        district_thread.start()
        
        print("\n✅ Both monitors started successfully!")
        print("\n" + "="*70)
        print("💡 MONITORING ACTIVE - Press Ctrl+C to stop")
        print("="*70)
        print("\n📊 Status updates will appear below:")
        print("-" * 70)
        
        # Track last check times
        last_status_display = time.time()
        
        # Keep the main thread alive and monitor thread health
        while True:
            time.sleep(10)
            
            # Display status every 5 minutes
            if time.time() - last_status_display > 300:  # 5 minutes
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"\n[{current_time}] 💚 System healthy - Both monitors running")
                last_status_display = time.time()
            
            # Check if both threads are still alive
            if not bookmyshow_thread.is_alive():
                logging.warning("⚠️ BookMyShow monitor thread died, restarting...")
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔄 Restarting BookMyShow monitor...")
                bookmyshow_thread = threading.Thread(target=run_bookmyshow_monitor, name="BookMyShow")
                bookmyshow_thread.start()
            
            if not district_thread.is_alive():
                logging.warning("⚠️ District.in monitor thread died, restarting...")
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔄 Restarting District.in monitor...")
                district_thread = threading.Thread(target=run_district_monitor, name="District.in")
                district_thread.start()
    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 SHUTTING DOWN MONITORS")
        print("="*70)
        print(f"Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Thank you for using Coolie Ticket Monitor!")
        print("="*70)
        logging.info("User requested shutdown")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        logging.error(f"Main execution error: {e}")

if __name__ == "__main__":
    main()
