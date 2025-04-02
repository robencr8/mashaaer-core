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
        # Get Twilio credentials
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.phone_number = os.environ.get("TWILIO_PHONE_NUMBER")
        
        # Set default owner phone number if not already set
        owner_phone = os.environ.get("OWNER_PHONE_NUMBER", "")
        if not owner_phone:
            # Use Roben's number as default
            roben_number = "+971522233989"
            os.environ["OWNER_PHONE_NUMBER"] = roben_number
            logger.info(f"Setting default owner phone number: {roben_number[:6]}XXXX")
        
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
            return {
                "success": False, 
                "error": error_msg,
                "solution": "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables."
            }
            
        # Clean up input by removing any spaces, dashes, or brackets
        if to_number:
            to_number = to_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Save original number for logging/reference
        original_number = to_number
        
        # Handle empty or None phone numbers
        if not to_number:
            error_msg = "No phone number provided"
            logger.error(error_msg)
            return {
                "success": False, 
                "error": error_msg,
                "solution": "Provide a valid recipient phone number in E.164 format (e.g., +971522233989)."
            }
        
        # Check if phone number is in proper format
        if not to_number.startswith('+'):
            logger.warning(f"Phone number {to_number} is not in E.164 format. Attempting to format...")
            
            # Handle all possible UAE number formats (more comprehensive)
            if to_number.startswith('0097'):
                # Convert 00971-style to +971
                to_number = '+' + to_number[2:]
                logger.info(f"Converted 00971 format to E.164: {to_number}")
            elif to_number.startswith('97') and len(to_number) >= 10:
                # Convert 971-style to +971
                to_number = '+' + to_number
                logger.info(f"Converted 971 format to E.164: {to_number}")
            elif to_number.startswith('05') and len(to_number) >= 9:
                # Convert UAE local format (05x) to international (+971 5x)
                to_number = '+971' + to_number[1:]
                logger.info(f"Converted UAE local format to E.164: {to_number}")
            elif to_number.startswith('5') and len(to_number) >= 8:
                # Handle bare UAE mobile numbers (5xxxxxxxx)
                to_number = '+971' + to_number
                logger.info(f"Converted UAE mobile number to E.164: {to_number}")
            elif to_number.startswith('00'):
                # Handle double-zero prefixed international format (instead of +)
                to_number = '+' + to_number[2:]
                logger.info(f"Converted 00 international format to E.164: {to_number}")
            # Handle Roben's specific number format if hard-coded
            elif to_number == "00971522233989" or to_number == "971522233989":
                to_number = "+971522233989"
                logger.info(f"Converted owner's number to E.164: {to_number}")
            elif to_number == "0522233989" or to_number == "522233989":
                to_number = "+971522233989"
                logger.info(f"Converted owner's number to E.164: {to_number}")
            else:
                # Generic fallback for other formats
                to_number = '+' + to_number
                logger.warning(f"Applied generic E.164 formatting: {to_number}, may not be correct")
            
            # Special handling for owner number (Roben Edwan)
            owner_number = os.environ.get("OWNER_PHONE_NUMBER", "")
            if owner_number and (original_number in ["roben", "owner", "admin", "me"] or to_number in ["roben", "owner", "admin", "me"]):
                to_number = owner_number
                logger.info(f"Using owner's number: {owner_number[:6]}XXXX")
            
            # Logging for the number transformation
            logger.info(f"Transformed phone number from '{original_number}' to '{to_number}'")
        
        # Validate the message text
        if not message_text:
            logger.warning("Empty message text provided, using a default message")
            message_text = "Alert from Robin AI"
        
        # Sanitize the phone number for logging (show only first 6 digits)
        sanitized_number = to_number[:6] + "XXXX" if len(to_number) > 6 else "XXXXXX"
        logger.info(f"Preparing to send SMS to {sanitized_number}")
        
        try:
            # Initialize Twilio client
            client = Client(self.account_sid, self.auth_token)
            
            # Log message length, which may affect pricing
            msg_length = len(message_text)
            segments = (msg_length + 159) // 160  # Calculate approx. number of segments
            logger.info(f"Message length: {msg_length} chars, approx. {segments} segment(s)")
            
            # Send the message
            message = client.messages.create(
                body=message_text,
                from_=self.phone_number,
                to=to_number
            )
            
            logger.info(f"SMS successfully sent to {sanitized_number}, SID: {message.sid}")
            return {
                "success": True, 
                "sid": message.sid, 
                "to": to_number,
                "from": self.phone_number,
                "segments": segments,
                "length": msg_length
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to send SMS to {sanitized_number}: {error_msg}")
            
            # Create detailed error response
            error_response = {
                "success": False,
                "error": "Failed to send SMS",
                "details": error_msg,
                "to": to_number,
                "original_number": original_number
            }
            
            # Check for specific error cases with detailed solutions
            if "21612" in error_msg:
                error_response["error"] = "Cannot send to this international number with trial account"
                error_response["solution"] = "Upgrade Twilio account or use a verified number. For trial accounts, add the recipient number to your Twilio Verified Numbers list in the Twilio Console."
                error_response["error_type"] = "trial_account_restriction"
            elif "21211" in error_msg:
                error_response["error"] = "Invalid phone number format"
                error_response["solution"] = "Ensure the phone number is in E.164 format (e.g., +971522233989). UAE mobile numbers should start with +971."
                error_response["error_type"] = "invalid_number_format"
                
                # Provide specific UAE number format examples
                if "971" in to_number:
                    error_response["uae_format_tip"] = "For UAE numbers, use format: +971XXXXXXXXX (e.g., +971522233989)"
            elif "21608" in error_msg:
                error_response["error"] = "Twilio account not authorized to send to this region"
                error_response["solution"] = "Set up geographic permissions in your Twilio account console for the UAE region."
                error_response["error_type"] = "geo_permission"
            elif "20003" in error_msg:
                error_response["error"] = "Authentication error: Invalid Twilio credentials"
                error_response["solution"] = "Check that TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables are set correctly."
                error_response["error_type"] = "auth_error"
            elif "21606" in error_msg:
                error_response["error"] = "The 'From' phone number is not a valid Twilio number"
                error_response["solution"] = "Verify the TWILIO_PHONE_NUMBER environment variable is set to a valid Twilio number owned by your account."
                error_response["error_type"] = "invalid_from_number"
            elif "30004" in error_msg:
                error_response["error"] = "Message content has been blocked by Twilio's spam filter"
                error_response["solution"] = "Modify the message content to comply with Twilio's messaging policies."
                error_response["error_type"] = "content_blocked"
            elif "30005" in error_msg:
                error_response["error"] = "Message rate limit exceeded"
                error_response["solution"] = "Slow down the rate of messages being sent to stay within Twilio's rate limits."
                error_response["error_type"] = "rate_limit"
            elif "30007" in error_msg:
                error_response["error"] = "Carrier blocked this message"
                error_response["solution"] = "The recipient's carrier may be blocking messages. Try a different phone number or contact Twilio support."
                error_response["error_type"] = "carrier_block"
            elif "30008" in error_msg:
                error_response["error"] = "Message delivery failed"
                error_response["solution"] = "The message could not be delivered. Verify the recipient number is correct and can receive SMS."
                error_response["error_type"] = "delivery_failure"
            
            # Add UAE-specific help if relevant
            if any(code in to_number for code in ['+971', '971', '05']):
                error_response["uae_number_info"] = {
                    "examples": ["+971522233989", "+971501234567"],
                    "format_info": "UAE mobile numbers start with '5' after the country code",
                    "transformation": f"Original: {original_number} → Processed: {to_number}"
                }
            
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
        # More comprehensive notification templates
        templates = {
            # Generic alerts and notifications
            'alert': "🚨 ROBIN AI ALERT: {message}",
            'reminder': "⏰ REMINDER: {message}",
            'update': "📊 UPDATE: {message}",
            'info': "ℹ️ INFO: {message}",
            
            # Emotion detection notifications
            'emotion': "😊 EMOTION DETECTED: {emotion} with confidence {confidence}%",
            'emotion_alert': "🔍 EMOTION ALERT: {emotion} detected at unusual intensity {confidence}%",
            
            # Face recognition notifications
            'face': "👤 FACE RECOGNIZED: {name} detected at {time}",
            'face_new': "👥 NEW FACE: Unknown person detected at {time}",
            'face_familiar': "👤 FAMILIAR FACE: {name} seen again after {days_since} days",
            
            # System notifications
            'security': "🔒 SECURITY: {message}",
            'system': "⚙️ SYSTEM: {message}",
            'error': "❌ ERROR: {message}",
            'status': "📡 STATUS: {message}",
            
            # Voice recognition notifications
            'voice': "🎤 VOICE DETECTED: {text}",
            'command': "🗣️ COMMAND: {command} was processed",
            
            # User interaction notifications
            'greeting': "👋 GREETING: {message}",
            'response': "💬 RESPONSE: {message}",
            
            # Learning notifications
            'learning': "🧠 LEARNING: {message}",
            
            # Special UAE locale notifications
            'uae_alert': "🇦🇪 UAE ALERT: {message}"
        }
        
        # Add level indicator for alerts if specified
        if notification_type == 'alert' and 'level' in kwargs:
            level = kwargs.get('level', '').upper()
            
            # Support multiple alert levels
            if level in ['WARNING', 'CRITICAL', 'INFO', 'ERROR', 'URGENT']:
                templates['alert'] = f"🚨 ROBIN AI {level} ALERT: {{message}}"
                
                # Add appropriate emoji based on level
                emojis = {
                    'WARNING': '⚠️',
                    'CRITICAL': '🔴',
                    'INFO': 'ℹ️',
                    'ERROR': '❌',
                    'URGENT': '🔥'
                }
                
                # Add the emoji at the beginning if available
                if level in emojis:
                    templates['alert'] = f"{emojis[level]} ROBIN AI {level} ALERT: {{message}}"
                
                # Add appropriate suffix based on level
                if level == 'CRITICAL':
                    kwargs['message'] = f"{kwargs.get('message', '')} Immediate attention required."
                elif level == 'URGENT':
                    kwargs['message'] = f"{kwargs.get('message', '')} Please respond ASAP."
                    
        # Add timestamp if requested
        if kwargs.get('include_timestamp', False):
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            timestamp_prefix = f"[{timestamp}] "
            
            # Remove the flag from kwargs to avoid template errors
            kwargs.pop('include_timestamp', None)
        else:
            timestamp_prefix = ""
            
        # Get the template for the notification type, fallback to a generic message if not found
        template = templates.get(notification_type, "📢 {message}")
        
        # Add the timestamp prefix if included
        template = timestamp_prefix + template
        
        try:
            # Generate the formatted message from the template
            logger.info(f"Preparing notification of type '{notification_type}'")
            
            # Check if required parameters are present
            required_params = []
            if '{message}' in template and 'message' not in kwargs:
                required_params.append('message')
            if '{emotion}' in template and 'emotion' not in kwargs:
                required_params.append('emotion')
            if '{name}' in template and 'name' not in kwargs:
                required_params.append('name')
            if '{time}' in template and 'time' not in kwargs:
                required_params.append('time')
                
            # If missing params, add defaults for common ones
            if required_params:
                logger.warning(f"Missing required parameters for {notification_type} template: {required_params}")
                
                # Add defaults for common parameters
                if 'emotion' in required_params:
                    kwargs['emotion'] = 'unknown'
                if 'confidence' in required_params:
                    kwargs['confidence'] = 70
                if 'name' in required_params:
                    kwargs['name'] = 'User'
                if 'time' in required_params:
                    from datetime import datetime
                    kwargs['time'] = datetime.now().strftime('%H:%M:%S')
                if 'message' in required_params:
                    kwargs['message'] = f"Robin AI {notification_type} notification"
            
            # Format the message with the provided parameters
            message = template.format(**kwargs)
            
            # Send the message
            logger.info(f"Sending {notification_type} notification")
            result = self.send_message(to_number, message)
            
            # Add notification metadata to the result
            if result["success"]:
                result["alert_type"] = notification_type
                result["notification_template"] = template
                result["notification_params"] = kwargs
            
            return result
            
        except KeyError as e:
            # Handle missing template parameters
            error_msg = f"Missing parameter in notification template: {str(e)}"
            logger.error(error_msg)
            
            # Try to send a fallback message
            try:
                fallback_message = f"ROBIN AI NOTIFICATION: {notification_type.upper()} - Unable to format complete message due to missing parameters."
                logger.warning(f"Sending fallback notification due to template error: {fallback_message}")
                
                result = self.send_message(to_number, fallback_message)
                result["alert_type"] = notification_type
                result["is_fallback"] = True
                result["missing_param"] = str(e)
                
                return result
                
            except Exception as fallback_error:
                # If even the fallback fails, return the error
                logger.error(f"Failed to send fallback notification: {str(fallback_error)}")
                
                return {
                    "success": False, 
                    "error": error_msg,
                    "alert_type": notification_type,
                    "fallback_error": str(fallback_error)
                }
        except Exception as e:
            # Handle other unexpected errors
            error_msg = f"Error sending notification: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False, 
                "error": error_msg,
                "alert_type": notification_type,
                "exception_type": type(e).__name__
            }
            
    def get_message_history(self, limit=10):
        """
        Get the recent message history from Twilio API.
        
        Args:
            limit (int): Maximum number of messages to retrieve
            
        Returns:
            list: A list of message dictionaries with status and metadata
        """
        # Check if credentials are available
        if not self.available:
            logger.warning("Cannot get message history: Twilio credentials not available")
            return []
            
        try:
            # Initialize Twilio client and try to get actual message history
            logger.info(f"Attempting to fetch message history from Twilio (limit: {limit})")
            client = Client(self.account_sid, self.auth_token)
            
            # Query the Twilio API for message history
            messages = []
            try:
                # Attempt to get actual messages from Twilio API
                twilio_messages = client.messages.list(limit=limit)
                
                # Process each message into our standard format
                for msg in twilio_messages:
                    sanitized_to = msg.to
                    if len(sanitized_to) > 6:
                        # Sanitize phone number in logs for privacy
                        display_to = sanitized_to[:6] + "XXXX"
                    else:
                        display_to = "XXXXXX"
                        
                    # Add to message list with more detailed info
                    messages.append({
                        "to": msg.to,
                        "display_to": display_to,
                        "from": msg.from_,
                        "status": msg.status,
                        "direction": msg.direction,
                        "body": msg.body,
                        "body_preview": msg.body[:50] + "..." if len(msg.body) > 50 else msg.body,
                        "date_sent": str(msg.date_sent) if msg.date_sent else None,
                        "date_created": str(msg.date_created) if msg.date_created else None,
                        "sid": msg.sid,
                        "price": msg.price,
                        "price_unit": msg.price_unit,
                        "error_code": msg.error_code,
                        "error_message": msg.error_message
                    })
                    
                logger.info(f"Successfully retrieved {len(messages)} message records from Twilio API")
                return messages
                
            except Exception as e:
                logger.error(f"Error fetching message history from Twilio API: {str(e)}")
                # If we get here, the API call failed, but we should still return something structured
                logger.warning("Returning empty message history due to API error")
                return []
                
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client for message history: {str(e)}")
            return []

# Example usage:
# twilio = TwilioHandler()
# if twilio.is_available():
#     twilio.send_message('+1234567890', 'Hello from Robin AI!')
#     twilio.send_notification('+1234567890', 'alert', message='Unusual activity detected')