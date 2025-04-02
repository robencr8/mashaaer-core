"""
Twilio SMS Helper for Mashaaer Feelings Mobile App
===================================================

This module provides functions to send SMS messages using the Twilio API.
For mobile app usage, it falls back to local SMS if Twilio is not available.
"""

import os
import requests
import json
from kivy.utils import platform


class TwilioHelper:
    """Helper class to send SMS notifications via Twilio or native Android SMS"""
    
    def __init__(self, server_url=None):
        """
        Initialize the Twilio Helper
        
        Args:
            server_url: URL of the Robin AI server with Twilio endpoint
        """
        self.server_url = server_url or "http://localhost:5000"
        self.account_sid = None
        self.auth_token = None
        self.from_number = None
    
    def configure(self, account_sid=None, auth_token=None, from_number=None):
        """Configure Twilio credentials directly in the app"""
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
    
    def is_configured(self):
        """Check if Twilio is properly configured"""
        return bool(self.account_sid and self.auth_token and self.from_number)
    
    def send_sms(self, to_number, message, use_server=True):
        """
        Send SMS message via Twilio
        
        Args:
            to_number: Recipient phone number in E.164 format
            message: SMS message text
            use_server: Whether to attempt to use the server's API first
            
        Returns:
            dict: Status information about the sent message
        """
        # First try to use the server API if available
        if use_server:
            try:
                result = self._send_via_server(to_number, message)
                if result and result.get("success"):
                    return {
                        "success": True,
                        "method": "server_api",
                        "details": result
                    }
            except Exception as e:
                print(f"Server SMS failed: {str(e)}")
        
        # If server fails or is not to be used, try direct Twilio API if configured
        if self.is_configured():
            try:
                result = self._send_via_direct_api(to_number, message)
                if result and result.get("success"):
                    return {
                        "success": True,
                        "method": "direct_api",
                        "details": result
                    }
            except Exception as e:
                print(f"Direct Twilio API failed: {str(e)}")
        
        # If all else fails, try to use native SMS on Android
        if platform == 'android':
            try:
                result = self._send_via_android(to_number, message)
                if result and result.get("success"):
                    return {
                        "success": True,
                        "method": "android_native",
                        "details": result
                    }
            except Exception as e:
                print(f"Android native SMS failed: {str(e)}")
        
        # If we get here, all methods have failed
        return {
            "success": False,
            "error": "All SMS methods failed",
            "methods_tried": ["server_api", "direct_api", "android_native"]
        }
    
    def _send_via_server(self, to_number, message):
        """Send SMS via the server API"""
        url = f"{self.server_url}/api/send-sms"
        payload = {
            "to": to_number,
            "message": message
        }
        
        response = requests.post(
            url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    
    def _send_via_direct_api(self, to_number, message):
        """Send SMS directly via Twilio API"""
        # This would use the Twilio Python SDK in a real implementation
        # For demonstration purposes, we'll use requests directly
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        auth = (self.account_sid, self.auth_token)
        payload = {
            "To": to_number,
            "From": self.from_number,
            "Body": message
        }
        
        response = requests.post(
            url,
            auth=auth,
            data=payload,
            timeout=10
        )
        
        if response.status_code == 201:  # Twilio returns 201 Created on success
            return {
                "success": True,
                "message_sid": response.json().get("sid"),
                "status": response.json().get("status")
            }
        else:
            return None
    
    def _send_via_android(self, to_number, message):
        """Send SMS using native Android capabilities"""
        # This would use pyjnius/plyer to access Android's SMS capabilities
        # For demonstration purposes, we'll simulate success
        
        try:
            # In a real implementation, this would use Android's SMS Manager
            # For example:
            # from plyer import sms
            # sms.send(recipient=to_number, message=message)
            
            # For demo purposes, we'll just print and return success
            print(f"[ANDROID SMS] To: {to_number}, Message: {message}")
            
            return {
                "success": True,
                "method": "android_native",
                "details": "SMS would be sent via Android SMS Manager"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_emotion_alert(self, to_number, primary_emotion, intensity, name=None):
        """
        Send an SMS alert about detected emotion
        
        Args:
            to_number: Recipient phone number
            primary_emotion: The primary emotion detected
            intensity: Emotion intensity (0-1)
            name: Optional name of the person
            
        Returns:
            dict: Status information about the sent message
        """
        person = name or "Person"
        intensity_percent = int(intensity * 100)
        
        message = f"Mashaaer Alert: {person} is feeling {primary_emotion.upper()} "
        message += f"with {intensity_percent}% intensity."
        
        if primary_emotion.lower() in ["sad", "angry", "fearful", "anxious"]:
            message += " They might need emotional support."
        
        return self.send_sms(to_number, message)


# Example usage
if __name__ == "__main__":
    helper = TwilioHelper()
    # Configure with your credentials
    helper.configure(
        account_sid="AC123...",
        auth_token="abc123...",
        from_number="+12345678901"
    )
    # Or use the server API
    result = helper.send_sms("+971522233989", "Hello from Mashaaer!")
    print(result)