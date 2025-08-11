#!/usr/bin/env python3
"""
Simple runner for Coolie Ticket Monitor
Works on all platforms (Windows, Mac, Linux)
"""

import os
import sys
import subprocess

def main():
    """Run the ticket monitor"""
    
    # Clear screen
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("="*50)
    print("🎬 COOLIE TICKET MONITOR - LAUNCHER")
    print("="*50)
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("\n❌ ERROR: .env file not found!")
        print("Please copy .env.template to .env and configure your settings.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Check for virtual environment
    venv_python = '.venv/bin/python3' if os.name == 'posix' else '.venv\\Scripts\\python.exe'
    
    if not os.path.exists('.venv'):
        print("\n📦 Setting up virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', '.venv'])
        
        print("📦 Installing dependencies...")
        pip_cmd = '.venv/bin/pip' if os.name == 'posix' else '.venv\\Scripts\\pip.exe'
        subprocess.run([pip_cmd, 'install', '-q', '-r', 'requirements.txt'])
        print("✅ Setup complete!\n")
    
    # Run the main monitor
    print("\n🚀 Starting monitors...\n")
    print("-"*50)
    
    try:
        # Run main.py using the virtual environment's Python
        subprocess.run([venv_python, 'main.py'])
    except KeyboardInterrupt:
        print("\n\n✅ Monitor stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()