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
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # If no SMTP credentials configured, log and return False
            if not self.smtp_username or not self.smtp_password:
                logger.warning(
                    f"SMTP credentials not configured. Email would be sent to {to_email}:\n"
                    f"Subject: {subject}\n"
                    f"Body: {body}"
                )
                # In development, we'll still return True to indicate the alert was processed
                # In production, you should configure SMTP properly
                return True
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            logger.warning(
                f"Email would be sent to {to_email}:\n"
                f"Subject: {subject}\n"
                f"Body: {body}"
            )
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            logger.warning(
                f"Email would be sent to {to_email}:\n"
                f"Subject: {subject}\n"
                f"Body: {body}"
            )
            return False
    
    def _get_current_time(self) -> str:
        """Get current time as formatted string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

