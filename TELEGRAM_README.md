# Telegram Notification System

The Telegram Notification System in Mashaaer Feelings provides real-time alerts and notifications about system events, errors, and user feedback through Telegram messenger.

## Features

- **Direct Notifications**: Send simple text messages to Telegram
- **System Notifications**: Send formatted notifications for system events
  - Startup notifications
  - Error alerts with severity levels
  - Usage statistics reports
  - Custom notifications with JSON content
- **Command-line Tool**: Easy-to-use utility for sending notifications from scripts
- **Web Interface**: Test interface for sending and testing notifications
- **API Endpoints**: RESTful API for programmatic access

## Setup

1. Create a Telegram bot through [BotFather](https://t.me/botfather) and get your bot token
2. Create a group or channel and add your bot to it
3. Find the chat ID of your group or channel
4. Set environment variables:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

## API Endpoints

### Direct Message

Send a simple message to Telegram.

**URL:** `/api/notifications/telegram/notify`  
**Method:** POST  
**Body:**
```json
{
  "message": "Your message here",
  "parse_mode": "Markdown"  // Optional, can be "Markdown" or "HTML"
}
```

### System Notification

Send a structured system notification.

**URL:** `/api/notifications/telegram/system`  
**Method:** POST  
**Body:**

For a startup notification:
```json
{
  "type": "startup",
  "data": {
    "version": "1.0",
    "env": "production"
  }
}
```

For an error notification:
```json
{
  "type": "error",
  "data": {
    "error_type": "DATABASE_ERROR",
    "details": "Connection to PostgreSQL failed",
    "severity": "high"  // can be "high", "medium", or "low"
  }
}
```

For a statistics notification:
```json
{
  "type": "stats",
  "data": {
    "users": 150,
    "interactions": 750,
    "api_calls": 3000
  }
}
```

For a custom notification:
```json
{
  "type": "custom",
  "data": {
    "title": "Custom Report",
    "content": {
      "key1": "value1",
      "key2": "value2",
      "nested": {
        "data": "example"
      }
    }
  }
}
```

### Status Check

Check if the Telegram notification system is configured and enabled.

**URL:** `/api/notifications/status`  
**Method:** GET  
**Response:**
```json
{
  "success": true,
  "enabled": true,
  "configured": true
}
```

## Command-line Tool

The `run_telegram_notification.py` script provides a convenient command-line interface for sending notifications.

### Usage Examples

Send a direct message:
```bash
python run_telegram_notification.py "Hello from Mashaaer Feelings!"
```

Send a startup notification:
```bash
python run_telegram_notification.py "System startup complete" --type=startup --version="2.5.0" --env="production"
```

Send an error notification:
```bash
python run_telegram_notification.py "Database connection failed" --type=error --error-type="DB_CONNECTION" --severity="high"
```

Send statistics:
```bash
python run_telegram_notification.py "Weekly stats" --type=stats --users=500 --interactions=2500 --api-calls=10000
```

Send a custom notification:
```bash
python run_telegram_notification.py "Custom data" --type=custom --title="Test Results" --content='{"passed": 45, "failed": 2}'
```

## Web Interface

A web interface for testing the Telegram notification system is available at:
```
/notify-telegram
```

This interface provides a user-friendly way to test different types of notifications with a visual form.

## Integration Examples

### Python Example

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

### JavaScript Example

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

1. Use appropriate notification types based on the context
2. Include relevant timestamps for important events
3. Set proper severity levels for error notifications
4. Use Markdown formatting for better readability
5. Include actionable information in error notifications
6. Implement rate limiting for high-frequency events
7. Secure your bot token and chat ID