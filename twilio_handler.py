"""
Twilio SMS Handler for Robin AI
===============================

This module handles sending SMS notifications using the Twilio API.
"""

import os
import logging
from typing import Dict, Any, Optional

# Import the Twilio REST client
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logging.warning("Twilio package not installed. SMS features will be disabled.")

# Set up logging
logger = logging.getLogger(__name__)


class TwilioHandler:
    """Handler for Twilio SMS integration"""

    def __init__(self):
        """Initialize the Twilio handler with credentials from environment variables"""
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.from_number = os.environ.get("TWILIO_PHONE_NUMBER")
        
        # Check if Twilio is properly configured
        self.is_configured = bool(
            TWILIO_AVAILABLE and 
            self.account_sid and 
            self.auth_token and 
            self.from_number
        )
        
        if self.is_configured:
            # Initialize the Twilio client
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("Twilio SMS handler initialized successfully")
        else:
            missing = []
            if not TWILIO_AVAILABLE:
                missing.append("Twilio package")
            if not self.account_sid:
                missing.append("TWILIO_ACCOUNT_SID")
            if not self.auth_token:
                missing.append("TWILIO_AUTH_TOKEN")
            if not self.from_number:
                missing.append("TWILIO_PHONE_NUMBER")
            
            logger.warning(f"Twilio SMS handler not properly configured. Missing: {', '.join(missing)}")

    def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """
        Send an SMS message via Twilio
        
        Args:
            to_number: The recipient's phone number (E.164 format preferred)
            message: The message text to send
            
        Returns:
            Dict with status information about the sent message
        """
        # Validate phone number format (basic check)
        to_number = self._validate_phone_number(to_number)
        
        if not self.is_configured:
            logger.error("Cannot send SMS: Twilio is not properly configured")
            return {
                "success": False,
                "error": "Twilio is not properly configured",
                "details": "Check environment variables and Twilio package installation"
            }
        
        try:
            # Send the message via Twilio
            twilio_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully to {to_number}, SID: {twilio_message.sid}")
            
            return {
                "success": True,
                "message_sid": twilio_message.sid,
                "status": twilio_message.status,
                "to": to_number,
                "from": self.from_number
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio API error: {str(e)}")
            return {
                "success": False,
                "error": "Twilio API error",
                "code": e.code,
                "details": str(e)
            }
            
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {str(e)}")
            return {
                "success": False,
                "error": "Unexpected error",
                "details": str(e)
            }

    def send_emotion_alert(
        self, 
        to_number: str, 
        primary_emotion: str, 
        intensity: float, 
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an SMS alert about detected emotion
        
        Args:
            to_number: Recipient phone number
            primary_emotion: The primary emotion detected
            intensity: Emotion intensity (0-1)
            name: Optional name of the person
            
        Returns:
            Dict with status information about the sent message
        """
        person = name or "Someone"
        intensity_percent = int(intensity * 100)
        
        message = f"Robin AI Alert: {person} is feeling {primary_emotion.upper()} "
        message += f"with {intensity_percent}% intensity."
        
        if primary_emotion.lower() in ["sad", "angry", "fearful", "anxious"]:
            message += " They might need emotional support."
        
        return self.send_sms(to_number, message)

    def _validate_phone_number(self, phone_number: str) -> str:
        """
        Validate and format phone number for Twilio
        
        Args:
            phone_number: The phone number to validate
            
        Returns:
            A properly formatted phone number
        """
        # Strip any whitespace
        phone_number = phone_number.strip()
        
        # Ensure it starts with + for E.164 format
        if not phone_number.startswith('+'):
            # Check if it starts with 00 (international format)
            if phone_number.startswith('00'):
                # Convert 00 prefix to + for E.164
                phone_number = '+' + phone_number[2:]
            else:
                # Add UAE country code as default if no international prefix
                # and doesn't start with 0 (assuming local UAE number)
                if not phone_number.startswith('0'):
                    phone_number = '+971' + phone_number
                else:
                    # Assume it's a UAE number starting with 0, replace 0 with +971
                    phone_number = '+971' + phone_number[1:]
        
        # Remove any remaining spaces or dashes
        phone_number = phone_number.replace(' ', '').replace('-', '')
        
        return phone_number

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the Twilio integration
        
        Returns:
            Dict with status information
        """
        return {
            "available": TWILIO_AVAILABLE,
            "configured": self.is_configured,
            "from_number": self.from_number if self.is_configured else None
        }


# Initialize the handler when imported
twilio_handler = TwilioHandler()

# Example usage
if __name__ == "__main__":
    # This is just for testing the module directly
    result = twilio_handler.send_sms(
        to_number="+971522233989",  # Example UAE number
        message="Test message from Robin AI"
    )
    print(result)