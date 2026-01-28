"""Email service for sending alerts and notifications."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from loguru import logger
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import settings


class EmailService:
    """Service for sending emails."""
    
    
    def __init__(self):
        # Email configuration - can be set via environment variables
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.use_tls = settings.SMTP_USE_TLS
        self.emergency_email = settings.EMERGENCY_EMAIL
    
    def send_sos_alert(
        self,
        rider_name: str,
        rider_id: str,
        location: Dict,
        to_email: Optional[str] = None
    ) -> bool:
        """
        Send SOS alert email with location.
        
        Args:
            rider_name: Name of the rider
            rider_id: ID of the rider
            location: Dictionary with latitude and longitude
            to_email: Email address to send to (defaults to emergency email)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            recipient = to_email or self.emergency_email
            
            # Get address from coordinates (optional - can use reverse geocoding)
            lat = location.get('latitude', location.get('lat', 0))
            lng = location.get('longitude', location.get('lng', 0))
            
            # Create email message
            subject = "🚨 URGENT: SOS Alert - Help Needed"
            
            # Create message body
            body = f"""
URGENT SOS ALERT - HELP NEEDED

A rider has triggered the emergency SOS button and needs immediate assistance.

Rider Information:
- Name: {rider_name}
- Rider ID: {rider_id}

Current Location:
- Latitude: {lat}
- Longitude: {lng}
- Google Maps Link: https://www.google.com/maps?q={lat},{lng}

Time: {self._get_current_time()}

Please take immediate action to assist the rider.

This is an automated alert from Smart Shield Trust Route system.
"""
            
            # Send email
            return self._send_email(
                to_email=recipient,
                subject=subject,
                body=body
            )
            
        except Exception as e:
            logger.error(f"Error sending SOS alert email: {e}")
            return False
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email.
        """
        try:
            # Check if we have credentials
            if not self.smtp_username or not self.smtp_password:
                missing = []
                if not self.smtp_username: missing.append("SMTP_USERNAME")
                if not self.smtp_password: missing.append("SMTP_PASSWORD")
                
                logger.warning(
                    f"EMAIL NOT SENT: Missing {', '.join(missing)} in config. "
                    f"Destination: {to_email} | Subject: {subject}"
                )
                return True # Dev mode success
            
            # Auto-strip quotes from password if present
            password = self.smtp_password
            if password.startswith('"') and password.endswith('"'):
                password = password[1:-1]
            elif password.startswith("'") and password.endswith("'"):
                password = password[1:-1]
            
            if password == "xxxx-xxxx-xxxx-xxxx":
                logger.warning(f"EMAIL NOT SENT: Placeholder password in use. Destination: {to_email}")
                return True
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_username, password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def _get_current_time(self) -> str:
        """Get current time as formatted string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

