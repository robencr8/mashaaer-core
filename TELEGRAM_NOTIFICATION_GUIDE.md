# Telegram Notification System Guide

## Overview

The Telegram Notification System provides a reliable way to send real-time alerts and notifications from the Mashaaer Feelings application to a designated Telegram channel or chat. This system is useful for:

- Monitoring system health
- Receiving error alerts
- Tracking usage statistics
- Sending custom notifications

## Setup

1. Create a Telegram bot using [BotFather](https://t.me/botfather)
2. Get your bot token
3. Create a channel or group and add your bot
4. Obtain the chat ID
5. Configure the following environment variables:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

## API Endpoints

### 1. Direct Notification

Send a simple message to Telegram.

**Endpoint:** `/api/notifications/telegram/notify`  
**Method:** POST  
**Content-Type:** application/json  

**Request Body:**
```json
{
  "message": "Your notification message", 
  "parse_mode": "Markdown"  // Optional, can be "Markdown" or "HTML"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Notification sent successfully",
  "timestamp": "2025-04-07T22:15:30.123456"
}
```

### 2. System Notification

Send formatted system notifications with predefined templates.

**Endpoint:** `/api/notifications/telegram/system`  
**Method:** POST  
**Content-Type:** application/json  

**Request Body (Startup):**
```json
{
  "type": "startup",
  "data": {
    "version": "1.0",
    "env": "production"
  }
}
```

**Request Body (Error):**
```json
{
  "type": "error",
  "data": {
    "error_type": "database_connection",
    "details": "Could not connect to PostgreSQL",
    "severity": "high"  // Can be "high", "medium", or "low"
  }
}
```

**Request Body (Stats):**
```json
{
  "type": "stats",
  "data": {
    "users": 100,
    "interactions": 500,
    "api_calls": 1000
  }
}
```

**Request Body (Custom):**
```json
{
  "type": "custom",
  "data": {
    "title": "Custom Title",
    "content": {
      "key1": "value1",
      "key2": "value2"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "System notification sent successfully",
  "timestamp": "2025-04-07T22:15:30.123456",
  "type": "startup"  // Reflects the notification type
}
```

### 3. System Status

Check if the Telegram notification system is properly configured and enabled.

**Endpoint:** `/api/notifications/status`  
**Method:** GET  

**Response:**
```json
{
  "success": true,
  "enabled": true,
  "configured": true
}
```

## Command-Line Tool

A command-line utility is provided for sending notifications directly from the terminal.

### Usage

```bash
# Send a direct message
python run_telegram_notification.py "Your message here"

# Send a startup notification
python run_telegram_notification.py "System started" --type=startup --version="2.5.0" --env="production"

# Send an error notification
python run_telegram_notification.py "Database error" --type=error --error-type="DB_CONNECTION" --severity="high"

# Send usage statistics
python run_telegram_notification.py "Daily stats" --type=stats --users=250 --interactions=1200 --api-calls=5000

# Send a custom notification
python run_telegram_notification.py "Custom message" --type=custom --title="Test Results" --content='{"passed": 45, "failed": 2}'
```

## Integration Examples

### Python Integration

```python
import requests

def send_telegram_notification(message):
    response = requests.post(
        "http://localhost:5000/api/notifications/telegram/notify",
        json={"message": message}
    )
    return response.json()

# Example usage
result = send_telegram_notification("Hello from Python!")
print(result)
```

### JavaScript Integration

```javascript
async function sendTelegramNotification(message) {
  const response = await fetch('http://localhost:5000/api/notifications/telegram/notify', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message })
  });
  return await response.json();
}

// Example usage
sendTelegramNotification('Hello from JavaScript!')
  .then(result => console.log(result));
```

## Best Practices

1. Use appropriate notification types for different scenarios
2. Include relevant details in error notifications
3. Don't overuse notifications to avoid alert fatigue
4. Use Markdown formatting for better readability
5. Consider using rate limiting for high-frequency events
6. Include timestamps in custom notifications for easier tracking

## Troubleshooting

1. Check that TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are correctly set
2. Verify that your bot has been added to the chat/channel
3. Ensure the bot has permission to post messages
4. Check the application logs for detailed error information
5. Test with the /api/notifications/status endpoint to verify configuration