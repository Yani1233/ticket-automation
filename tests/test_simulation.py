#!/usr/bin/env python3

"""Simulate a ticket availability alert for testing"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ticket_alert import TicketAlert

class SimulatedAlert(TicketAlert):
    def check_platform(self, platform):
        """Override to simulate ticket availability"""
        platform_name = platform['name']
        
        # Simulate that tickets are available for testing
        print(f"🎭 Simulating ticket availability for {platform_name}")
        return True  # Always return True to trigger alert

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🎬 Simulating Ticket Alert for Coolie")
    print("=" * 60)
    
    # Use the simulated alert system
    alert_system = SimulatedAlert()
    
    # Use a different state file to avoid conflicts
    alert_system.state_file = 'simulation_state.json'
    
    # Run the check - this will trigger alerts
    print("\n📧 This will send a real email alert to test the system...")
    alert_system.run_check()
    
    print("\n✅ Simulation complete! Check your email for the alert.")