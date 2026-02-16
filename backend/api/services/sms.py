"""Twilio SMS service for emergency alerts."""
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from config.config import settings
from loguru import logger
import os

class SMSService:
    """Service for sending SMS alerts via Twilio."""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_phone = settings.TWILIO_PHONE_NUMBER
        
        self.enabled = bool(self.account_sid and self.auth_token and self.from_phone)
        
        if self.enabled:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("SMSService initialized with Twilio")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.enabled = False
        else:
            logger.warning("Twilio credentials missing. SMS service disabled.")

    async def send_sms(self, to_phone: str, message: str) -> bool:
        """Send an SMS message."""
        if not self.enabled:
            logger.warning(f"SMS service disabled. Would have sent to {to_phone}: {message}")
            return False
            
        try:
            # We use trial accounts usually start with + for Twilio
            # Simplified for now, in production use event loop for blocking calls if needed
            # but usually Twilio is fast enough or use run_in_executor
            import asyncio
            
            loop = asyncio.get_event_loop()
            message_instance = await loop.run_in_executor(
                None, 
                lambda: self.client.messages.create(
                    body=message,
                    from_=self.from_phone,
                    to=to_phone
                )
            )
            logger.info(f"SMS sent to {to_phone}: SID {message_instance.sid}")
            return True
        except TwilioRestException as e:
            logger.error(f"Twilio error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False

    async def send_emergency_alert(self, rider_name: str, location_str: str, emergency_type: str = "SOS") -> bool:
        """Send an emergency alert to the configured emergency contact."""
        target_phone = settings.EMERGENCY_PHONE
        if not target_phone:
            logger.warning("No emergency phone configured")
            return False
            
        msg = f"🚨 {emergency_type} ALERT! Rider {rider_name} triggered emergency at {location_str}. Help needed immediately!"
        return await self.send_sms(target_phone, msg)

# Singleton instance
sms_service = SMSService()
