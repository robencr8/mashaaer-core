"""
Telegram Notification System for Mashaaer Feelings
Provides functionality to send notifications about system events to Telegram
"""
import os
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

class TelegramNotifier:
    """
    Manages sending notifications to a Telegram channel or chat
    for important system events and updates
    """
    
    def __init__(self):
        """Initialize the Telegram notifier with configuration"""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", 
                            "7664942391:AAGobNjnvGrMOZTtL_b6g0T80DvAzrOu_LI")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "7769852671")
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if self.enabled:
            logger.info("Telegram notification system initialized")
        else:
            logger.warning("Telegram notification system disabled: missing token or chat ID")
    
    def send_message(self, message: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        """
        Send a message to the configured Telegram chat
        
        Args:
            message: The message text to send
            parse_mode: Message format ('Markdown' or 'HTML')
            
        Returns:
            Dict with success status and response details
        """
        if not self.enabled:
            logger.warning("Attempted to send Telegram message while disabled")
            return {"success": False, "error": "Telegram notifications disabled"}
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Telegram message sent successfully")
            return {
                "success": True,
                "response": response.json(),
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def send_system_startup(self, version: str = "1.0", env: str = "production") -> Dict[str, Any]:
        """Send notification that system has started up"""
        message = f"""
🚀 *Mashaaer System Startup*
- Version: `{version}`
- Environment: `{env}`
- Time: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
- Status: Online and ready
        """
        return self.send_message(message)
    
    def send_error_alert(self, error_type: str, details: str, severity: str = "high") -> Dict[str, Any]:
        """Send notification about a system error"""
        emoji = "🔴" if severity == "high" else "🟠" if severity == "medium" else "🟡"
        message = f"""
{emoji} *System Error Alert*
- Type: `{error_type}`
- Severity: `{severity}`
- Time: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
- Details: `{details}`
        """
        return self.send_message(message)
    
    def send_usage_stats(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Send system usage statistics"""
        message = f"""
📊 *Mashaaer Usage Statistics*
- Total Users: `{stats.get('users', 0)}`
- Interactions: `{stats.get('interactions', 0)}`
- API Calls: `{stats.get('api_calls', 0)}`
- Time: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
        """
        return self.send_message(message)
    
    def send_custom_notification(self, title: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Send a custom formatted notification"""
        message_lines = [f"💬 *{title}*"]
        
        for key, value in content.items():
            message_lines.append(f"- {key}: `{value}`")
        
        message_lines.append(f"- Time: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
        
        return self.send_message("\n".join(message_lines))

# Create a global instance for easy import
notifier = TelegramNotifier()

def send_telegram_notification(message: str) -> Dict[str, Any]:
    """
    Convenience function to send a simple notification
    
    Args:
        message: The message to send
        
    Returns:
        Dict with success status and response
    """
    return notifier.send_message(message)

# Command-line execution for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        result = send_telegram_notification(message)
        print("✅ Message sent" if result["success"] else f"❌ Failed: {result.get('error')}")
    else:
        # Test startup notification
        result = notifier.send_system_startup(version="1.1", env="development")
        print("✅ System startup notification sent" if result["success"] else f"❌ Failed: {result.get('error')}")