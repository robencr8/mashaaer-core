"""
Twilio API Integration for Robin AI
Provides direct API access to Twilio services for SMS messaging
"""

import os
import json
import logging
import requests
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

def is_twilio_configured():
    """Check if Twilio credentials are properly configured"""
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_PHONE_NUMBER')
    
    return all([account_sid, auth_token, from_number])

def send_sms(to_number, message):
    """
    Send an SMS message via Twilio API
    
    Args:
        to_number (str): The recipient's phone number
        message (str): The message to send
        
    Returns:
        dict: The Twilio API response or None if failed
    """
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_PHONE_NUMBER')

    if not all([account_sid, auth_token, from_number]):
        logger.error("Twilio environment variables not set.")
        return None

    # Format UAE phone numbers if needed
    to_number = format_uae_number(to_number)

    url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
    data = {
        'To': to_number,
        'From': from_number,
        'Body': message
    }
    auth = (account_sid, auth_token)
    
    try:
        response = requests.post(url, data=data, auth=auth)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        result = response.json()
        
        # Log the message to the database or file
        log_message(to_number, message, result.get('sid', 'unknown'))
        
        logger.info(f"SMS sent successfully to {to_number}")
        return result
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending SMS: {e}")
        return None

def send_notification(to_number, title, message, level="info"):
    """
    Send a formatted notification message
    
    Args:
        to_number (str): The recipient's phone number
        title (str): Notification title
        message (str): Notification message
        level (str): Notification level (info, warning, alert)
        
    Returns:
        dict: The Twilio API response or None if failed
    """
    # Prepare the formatted message with title and timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format based on notification level
    if level.lower() == "warning":
        prefix = "⚠️ WARNING"
    elif level.lower() == "alert":
        prefix = "🚨 ALERT"
    else:
        prefix = "ℹ️ INFO"
    
    formatted_message = f"{prefix}: {title}\n\n{message}\n\nTimestamp: {timestamp}"
    
    # Send the formatted message
    return send_sms(to_number, formatted_message)

def get_message_history(limit=10):
    """
    Get message history from the logs
    
    Args:
        limit (int): Maximum number of messages to return
        
    Returns:
        list: List of message records
    """
    try:
        log_file = os.path.join(os.getcwd(), 'logs', 'sms_messages.json')
        
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, 'r') as f:
            messages = json.load(f)
            
        # Sort by timestamp (descending) and limit
        messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return messages[:limit]
    
    except Exception as e:
        logger.error(f"Error retrieving message history: {e}")
        return []

def format_uae_number(phone_number):
    """
    Format UAE phone numbers to the correct international format
    
    Args:
        phone_number (str): The phone number to format
        
    Returns:
        str: The properly formatted phone number
    """
    # Remove any spaces, dashes, or parentheses
    clean_number = ''.join(filter(str.isdigit, phone_number))
    
    # Handle UAE numbers
    if clean_number.startswith('0') and len(clean_number) == 10:  # 05xxxxxxxx
        return '+971' + clean_number[1:]
    elif clean_number.startswith('5') and len(clean_number) == 9:  # 5xxxxxxxx
        return '+971' + clean_number
    elif clean_number.startswith('971') and not clean_number.startswith('+'):
        return '+' + clean_number
    elif not clean_number.startswith('+'):
        return '+' + clean_number
    
    return phone_number

def log_message(to_number, message, message_sid):
    """
    Log the sent message to a JSON file
    
    Args:
        to_number (str): The recipient's phone number
        message (str): The message that was sent
        message_sid (str): The Twilio message SID
    """
    try:
        # Ensure logs directory exists
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'sms_messages.json')
        
        # Create a new message record
        message_record = {
            'to': to_number,
            'message': message,
            'sid': message_sid,
            'timestamp': datetime.now().isoformat()
        }
        
        # Load existing messages or create new list
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    messages = json.load(f)
                except json.JSONDecodeError:
                    messages = []
        else:
            messages = []
        
        # Add new message and save
        messages.append(message_record)
        
        with open(log_file, 'w') as f:
            json.dump(messages, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error logging SMS message: {e}")