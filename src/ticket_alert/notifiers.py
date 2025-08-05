"""Notification modules for ticket alerts"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict

logger = logging.getLogger(__name__)


class BaseNotifier(ABC):
    """Base class for all notifiers"""
    
    @abstractmethod
    def send(self, platform_name: str, url: str) -> bool:
        """Send notification"""
        pass


class EmailNotifier(BaseNotifier):
    """Email notification handler"""
    
    def __init__(self, config: Dict):
        self.config = config
        
    def send(self, platform_name: str, url: str) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['from_email']
            msg['To'] = self.config['to_email']
            msg['Subject'] = f"🎬 Coolie (Tamil) Tickets Available on {platform_name}!"
            
            body = self._create_email_body(platform_name, url)
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['from_email'], self.config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email alert sent successfully for {platform_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def _create_email_body(self, platform_name: str, url: str) -> str:
        """Create formatted email body"""
        return f"""
🎉 Great news! Tickets for "Coolie (Tamil)" are now available on {platform_name}!

🔗 Book now: {url}

📍 Location: Bengaluru
🎭 Movie: Coolie (Tamil)
⏰ Alert sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Don't wait - book your tickets now before they sell out!

---
Automated ticket alert system
        """.strip()


class SlackNotifier(BaseNotifier):
    """Slack notification handler (future implementation)"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        
    def send(self, platform_name: str, url: str) -> bool:
        # TODO: Implement Slack notifications
        logger.info("Slack notifications not yet implemented")
        return False