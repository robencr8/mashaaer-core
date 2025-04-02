"""
Twilio SMS Handler for Robin AI
Handles sending SMS notifications using the Twilio API
"""
import os
import logging
from twilio.rest import Client

# Setup logging
logger = logging.getLogger(__name__)

class TwilioHandler:
    """Handles sending SMS notifications via Twilio"""
    
    def __init__(self):
        """Initialize the Twilio handler with credentials from environment variables"""
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.phone_number = os.environ.get("TWILIO_PHONE_NUMBER")
        
        # Check if credentials are available
        self.available = all([self.account_sid, self.auth_token, self.phone_number])
        
        if not self.available:
            logger.warning("Twilio credentials not found. SMS notifications will not be available.")
        else:
            logger.info("Twilio SMS handler initialized successfully.")
    
    def is_available(self):
        """Check if Twilio SMS service is available"""
        return self.available
    
    def send_message(self, to_number, message_text):
        """
        Send an SMS message using Twilio
        
        Args:
            to_number (str): The recipient's phone number in E.164 format (+1XXXXXXXXXX)
            message_text (str): The message content to send
            
        Returns:
            bool: True if the message was sent successfully, False otherwise
        """
        if not self.available:
            logger.error("Cannot send SMS: Twilio credentials not available")
            return False
        
        # Check if phone number is in proper format
        if not to_number.startswith('+'):
            logger.warning(f"Phone number {to_number} is not in E.164 format. Adding +1 prefix.")
            to_number = '+1' + to_number.lstrip('1')
        
        try:
            # Initialize Twilio client
            client = Client(self.account_sid, self.auth_token)
            
            # Send the message
            message = client.messages.create(
                body=message_text,
                from_=self.phone_number,
                to=to_number
            )
            
            logger.info(f"SMS sent to {to_number}, SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    def send_notification(self, to_number, notification_type, **kwargs):
        """
        Send a pre-formatted notification based on the notification type
        
        Args:
            to_number (str): The recipient's phone number in E.164 format
            notification_type (str): The type of notification ('alert', 'reminder', etc.)
            **kwargs: Additional parameters specific to the notification type
            
        Returns:
            bool: True if the notification was sent successfully, False otherwise
        """
        templates = {
            'alert': "🚨 ROBIN AI ALERT: {message}",
            'reminder': "⏰ REMINDER: {message}",
            'update': "📊 UPDATE: {message}",
            'emotion': "😊 EMOTION DETECTED: {emotion} with confidence {confidence}%",
            'face': "👤 FACE RECOGNIZED: {name} detected at {time}",
            'security': "🔒 SECURITY: {message}"
        }
        
        template = templates.get(notification_type, "{message}")
        
        try:
            message = template.format(**kwargs)
            return self.send_message(to_number, message)
        except KeyError as e:
            logger.error(f"Missing parameter in notification template: {str(e)}")
            return False

# Example usage:
# twilio = TwilioHandler()
# if twilio.is_available():
#     twilio.send_message('+1234567890', 'Hello from Robin AI!')
#     twilio.send_notification('+1234567890', 'alert', message='Unusual activity detected')