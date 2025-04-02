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
            dict: A dictionary with status information and any error details
        """
        if not self.available:
            error_msg = "Cannot send SMS: Twilio credentials not available"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Check if phone number is in proper format
        if not to_number.startswith('+'):
            logger.warning(f"Phone number {to_number} is not in E.164 format. Adding + prefix.")
            # UAE numbers should start with +971
            if to_number.startswith('0097'):
                to_number = '+' + to_number[2:]
            elif to_number.startswith('97'):
                to_number = '+' + to_number
            else:
                to_number = '+' + to_number
        
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
            return {"success": True, "sid": message.sid, "to": to_number}
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to send SMS: {error_msg}")
            
            # Provide more specific error messages for common Twilio errors
            error_response = {
                "success": False,
                "error": "Failed to send SMS",
                "details": error_msg,
                "to": to_number
            }
            
            # Check for specific error cases
            if "21612" in error_msg:
                error_response["error"] = "Cannot send to this international number with trial account"
                error_response["solution"] = "Upgrade Twilio account or use a verified number"
            elif "21211" in error_msg:
                error_response["error"] = "Invalid phone number format"
            elif "21608" in error_msg:
                error_response["error"] = "Twilio account not authorized to send to this region"
            
            return error_response
    
    def send_notification(self, to_number, notification_type, **kwargs):
        """
        Send a pre-formatted notification based on the notification type
        
        Args:
            to_number (str): The recipient's phone number in E.164 format
            notification_type (str): The type of notification ('alert', 'reminder', etc.)
            **kwargs: Additional parameters specific to the notification type
            
        Returns:
            dict: A dictionary with status information and any error details
        """
        templates = {
            'alert': "🚨 ROBIN AI ALERT: {message}",
            'reminder': "⏰ REMINDER: {message}",
            'update': "📊 UPDATE: {message}",
            'emotion': "😊 EMOTION DETECTED: {emotion} with confidence {confidence}%",
            'face': "👤 FACE RECOGNIZED: {name} detected at {time}",
            'security': "🔒 SECURITY: {message}",
            'system': "⚙️ SYSTEM: {message}"
        }
        
        # Add level indicator for alerts if specified
        if notification_type == 'alert' and 'level' in kwargs:
            level = kwargs.get('level', '').upper()
            if level in ['WARNING', 'CRITICAL', 'INFO']:
                templates['alert'] = f"🚨 ROBIN AI {level} ALERT: {{message}}"
                
                # Add immediate attention note for critical alerts
                if level == 'CRITICAL':
                    kwargs['message'] = f"{kwargs.get('message', '')} Immediate attention required."
        
        template = templates.get(notification_type, "{message}")
        
        try:
            message = template.format(**kwargs)
            result = self.send_message(to_number, message)
            if result["success"]:
                result["alert_type"] = notification_type
            return result
        except KeyError as e:
            error_msg = f"Missing parameter in notification template: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False, 
                "error": error_msg,
                "alert_type": notification_type
            }
            
    def get_message_history(self):
        """
        Get the recent message history (placeholder for future implementation)
        
        Returns:
            list: A list of message dictionaries with status and metadata
        """
        # This would typically make an API call to Twilio to fetch message history
        # For now, we'll return a placeholder response
        
        if not self.available:
            logger.warning("Cannot get message history: Twilio credentials not available")
            return []
            
        # Placeholder for message history
        # In a real implementation, we would fetch this from the Twilio API
        return [
            {
                "to": "+1234567890",
                "status": "delivered", 
                "body": "Welcome to Robin AI! Your personal AI assistant is ready.",
                "date_sent": "2025-04-02T08:30:00Z",
                "sid": "SM123456789"
            }
        ]

# Example usage:
# twilio = TwilioHandler()
# if twilio.is_available():
#     twilio.send_message('+1234567890', 'Hello from Robin AI!')
#     twilio.send_notification('+1234567890', 'alert', message='Unusual activity detected')