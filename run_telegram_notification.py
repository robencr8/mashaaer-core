#!/usr/bin/env python3
"""
Run Telegram notification script for Mashaaer Feelings
Simple command-line utility to send notifications to Telegram from the console
"""
import sys
import requests
import json
import argparse
from typing import Dict, Any, Optional
from datetime import datetime

def send_notification(message: str, notification_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Send a notification to Telegram
    
    Args:
        message: The message to send for a direct notification
        notification_type: Optional type of notification (startup, error, stats, custom)
        **kwargs: Additional arguments specific to the notification type
    
    Returns:
        Dict with the API response
    """
    base_url = "http://localhost:5000/api/notifications"
    
    # Direct message notification
    if notification_type is None:
        url = f"{base_url}/telegram/notify"
        payload = {
            "message": message,
            "parse_mode": "Markdown"
        }
    # System notification
    else:
        url = f"{base_url}/telegram/system"
        if notification_type == "startup":
            payload = {
                "type": "startup",
                "data": {
                    "version": kwargs.get("version", "1.0"),
                    "env": kwargs.get("env", "production")
                }
            }
        elif notification_type == "error":
            payload = {
                "type": "error",
                "data": {
                    "error_type": kwargs.get("error_type", "generic_error"),
                    "details": kwargs.get("details", message),
                    "severity": kwargs.get("severity", "high")
                }
            }
        elif notification_type == "stats":
            payload = {
                "type": "stats",
                "data": {
                    "users": kwargs.get("users", 0),
                    "interactions": kwargs.get("interactions", 0),
                    "api_calls": kwargs.get("api_calls", 0)
                }
            }
        elif notification_type == "custom":
            payload = {
                "type": "custom",
                "data": {
                    "title": kwargs.get("title", "Custom Notification"),
                    "content": kwargs.get("content", {"message": message})
                }
            }
        else:
            print(f"❌ Invalid notification type: {notification_type}")
            return {"success": False, "error": "Invalid notification type"}
    
    # Send the request
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get("success", False):
            print(f"✅ Notification sent successfully")
        else:
            print(f"❌ Failed to send notification: {result.get('error', 'Unknown error')}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Main function to parse arguments and send notifications"""
    parser = argparse.ArgumentParser(description="Send Telegram notifications for Mashaaer Feelings")
    
    # Add arguments
    parser.add_argument("message", help="The message to send (or main content for notification types)")
    parser.add_argument("--type", choices=["direct", "startup", "error", "stats", "custom"], 
                        default="direct", help="The type of notification to send")
    parser.add_argument("--version", default="1.0", help="Version number for startup notifications")
    parser.add_argument("--env", default="production", help="Environment for startup notifications")
    parser.add_argument("--error-type", default="generic_error", help="Error type for error notifications")
    parser.add_argument("--severity", choices=["high", "medium", "low"], 
                        default="high", help="Error severity for error notifications")
    parser.add_argument("--users", type=int, default=0, help="User count for stats notifications")
    parser.add_argument("--interactions", type=int, default=0, help="Interaction count for stats notifications")
    parser.add_argument("--api-calls", type=int, default=0, help="API call count for stats notifications")
    parser.add_argument("--title", default="Custom Notification", help="Title for custom notifications")
    parser.add_argument("--content", default="{}", help="JSON content for custom notifications (as string)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Prepare additional arguments
    kwargs = {
        "version": args.version,
        "env": args.env,
        "error_type": args.error_type,
        "severity": args.severity,
        "users": args.users,
        "interactions": args.interactions,
        "api_calls": args.api_calls,
        "title": args.title
    }
    
    # Parse custom content if provided
    if args.type == "custom":
        try:
            kwargs["content"] = json.loads(args.content)
        except json.JSONDecodeError:
            print("❌ Invalid JSON for content. Using default.")
            kwargs["content"] = {"message": args.message}
    
    # Send notification
    notification_type = None if args.type == "direct" else args.type
    result = send_notification(args.message, notification_type, **kwargs)
    
    # Print result
    if result.get("success", False):
        timestamp = result.get("timestamp", datetime.now().isoformat())
        print(f"Sent at: {timestamp}")
    
    return 0 if result.get("success", False) else 1

if __name__ == "__main__":
    sys.exit(main())