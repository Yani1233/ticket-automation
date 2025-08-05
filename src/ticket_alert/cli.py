"""Command-line interface for ticket alert system"""

import sys
import os
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
from .core import TicketAlert

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/ticket_alert.log', mode='a'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description="Monitor movie ticket availability and send alerts"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="configs/coolie.yaml",
        help="Path to configuration file (default: configs/coolie.yaml)"
    )
    
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run check once and exit (default: continuous monitoring)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--test-email",
        action="store_true",
        help="Send a test email to verify configuration"
    )
    
    args = parser.parse_args()
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Setup logging
    setup_logging(args.verbose)
    
    try:
        if args.test_email:
            # Test email functionality
            from .notifiers import EmailNotifier
            email_config = {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'from_email': os.getenv('EMAIL_FROM'),
                'to_email': os.getenv('EMAIL_TO'),
                'password': os.getenv('EMAIL_PASSWORD')
            }
            
            notifier = EmailNotifier(email_config)
            if notifier.send("Test Platform", "https://example.com"):
                print("✅ Test email sent successfully!")
            else:
                print("❌ Failed to send test email. Check logs for details.")
            return
        
        # Create alert system
        alert_system = TicketAlert(config_path=args.config)
        
        # Run monitoring
        if args.once:
            logger.info("Running single check...")
            alert_system.run_check()
        else:
            logger.info("Starting continuous monitoring...")
            alert_system.run_continuous()
            
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()