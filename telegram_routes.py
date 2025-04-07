"""
Telegram Notification Routes for Mashaaer Feelings
Provides endpoints for sending system notifications via Telegram
"""
from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any
from telegram_notifier import notifier, send_telegram_notification

# Set up logging
logger = logging.getLogger(__name__)

# Create a Flask Blueprint for telegram routes
telegram_bp = Blueprint('telegram', __name__, url_prefix='/api/notifications')

@telegram_bp.route('/telegram/notify', methods=['POST'])
def telegram_notify():
    """
    Send a notification via Telegram
    
    Request body:
    {
        "message": "Your notification message", 
        "parse_mode": "Markdown" or "HTML" (optional)
    }
    
    Returns:
    {
        "success": true,
        "message": "Notification sent successfully",
        "timestamp": "2025-04-07T22:15:30.123456"
    }
    """
    try:
        data = request.get_json()
        message = data.get('message')
        parse_mode = data.get('parse_mode', 'Markdown')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        # Send the notification
        result = send_telegram_notification(message)
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": "Notification sent successfully",
                "timestamp": result['timestamp']
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', 'Unknown error')
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@telegram_bp.route('/telegram/system', methods=['POST'])
def system_notification():
    """
    Send a system notification via Telegram
    
    Request body:
    {
        "type": "startup" | "error" | "stats" | "custom",
        "data": {
            // For startup:
            "version": "1.0", 
            "env": "production"
            
            // For error:
            "error_type": "database_connection",
            "details": "Could not connect to PostgreSQL",
            "severity": "high" | "medium" | "low"
            
            // For stats:
            "users": 100,
            "interactions": 500,
            "api_calls": 1000
            
            // For custom:
            "title": "Custom Title",
            "content": {
                "key1": "value1",
                "key2": "value2"
            }
        }
    }
    
    Returns:
    {
        "success": true,
        "message": "System notification sent successfully",
        "timestamp": "2025-04-07T22:15:30.123456",
        "type": "startup" | "error" | "stats" | "custom"
    }
    """
    try:
        data = request.get_json()
        notification_type = data.get('type')
        notification_data = data.get('data', {})
        
        if not notification_type:
            return jsonify({
                "success": False,
                "error": "Notification type is required"
            }), 400
        
        result = {}
        
        # Route to the appropriate notification method based on type
        if notification_type == 'startup':
            version = notification_data.get('version', '1.0')
            env = notification_data.get('env', 'production')
            result = notifier.send_system_startup(version=version, env=env)
        
        elif notification_type == 'error':
            error_type = notification_data.get('error_type', 'unknown')
            details = notification_data.get('details', 'No details provided')
            severity = notification_data.get('severity', 'high')
            result = notifier.send_error_alert(error_type=error_type, details=details, severity=severity)
        
        elif notification_type == 'stats':
            result = notifier.send_usage_stats(stats=notification_data)
        
        elif notification_type == 'custom':
            title = notification_data.get('title', 'Custom Notification')
            content = notification_data.get('content', {})
            result = notifier.send_custom_notification(title=title, content=content)
        
        else:
            return jsonify({
                "success": False,
                "error": f"Unknown notification type: {notification_type}"
            }), 400
        
        if result.get('success', False):
            return jsonify({
                "success": True,
                "message": "System notification sent successfully",
                "timestamp": result['timestamp'],
                "type": notification_type
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', 'Unknown error')
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending system notification: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@telegram_bp.route('/status', methods=['GET'])
def telegram_status():
    """
    Get the status of the Telegram notification system
    
    Returns:
    {
        "success": true,
        "enabled": true,
        "configured": true
    }
    """
    try:
        return jsonify({
            "success": True,
            "enabled": notifier.enabled,
            "configured": bool(notifier.bot_token and notifier.chat_id)
        })
    except Exception as e:
        logger.error(f"Error getting Telegram status: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Register an additional shorter endpoint for easier access
@telegram_bp.route('/', methods=['GET'])
def telegram_index():
    """Shorthand endpoint that returns the same as /status"""
    return telegram_status()

def init_telegram_notification_api(app):
    """
    Initialize Telegram notification API routes
    
    Args:
        app: The Flask application instance
    
    Returns:
        The telegram blueprint
    """
    try:
        app.register_blueprint(telegram_bp)
        logger.info("Telegram notification routes registered successfully")
        
        # Send a startup notification
        try:
            env = app.config.get('ENV', 'development')
            notifier.send_system_startup(version="1.0", env=env)
        except Exception as e:
            logger.warning(f"Could not send startup notification: {str(e)}")
            
        return telegram_bp
    except Exception as e:
        logger.error(f"Error initializing Telegram notification routes: {str(e)}")
        raise