#!/usr/bin/env python3
"""
Simple continuous monitor for Coolie tickets
Runs every 5 minutes without cron
"""

import time
import subprocess
import sys
from datetime import datetime

def run_monitor():
    """Run the monitor and display results"""
    print(f"\n{'='*60}")
    print(f"🎬 Checking at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)
    
    try:
        # Run the monitor script
        result = subprocess.run(
            [sys.executable, "bookmyshow_monitor.py", "--once"],
            capture_output=True,
            text=True
        )
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("🎬 COOLIE TICKET MONITOR - CONTINUOUS MODE")
    print("Checking every 5 minutes")
    print("Press Ctrl+C to stop")
    print("")
    
    while True:
        try:
            run_monitor()
            print(f"\n💤 Sleeping for 5 minutes... Next check at {(datetime.now().timestamp() + 300)}")
            time.sleep(300)  # 5 minutes

        except KeyboardInterrupt:
            print("\n\n🛑 Monitor stopped")
            break

if __name__ == "__main__":
    main()