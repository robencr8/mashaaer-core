"""
Admin Routes for Mashaaer Feelings Application
Provides admin dashboard and management features
"""
from flask import Blueprint, render_template, request, jsonify, current_app
import logging
import json
import os
import datetime
from typing import Dict, Any, List, Optional

# Import components
from rules_config_loader import RulesConfigLoader
from log_manager import get_recent_interactions, get_emotion_statistics, get_action_statistics, clear_logs
from memory_store import get_all_user_memories

# Set up logging
logger = logging.getLogger(__name__)

# Create Blueprint
admin_bp = Blueprint('admin', __name__)

# Initialize rules config loader
rules_loader = RulesConfigLoader()

@admin_bp.route('/admin')
def admin():
    """
    Admin dashboard page
    Shows rules, logs, and system statistics
    """
    try:
        # Get rules
        rules = rules_loader.get_rules()
        
        # Get recent logs
        logs = get_recent_interactions(limit=50)
        
        # Get emotion statistics
        emotion_stats = get_emotion_statistics()
        
        # Get action statistics
        action_stats = get_action_statistics()
        
        return render_template(
            'admin.html', 
            rules=rules, 
            logs=logs,
            emotion_stats=emotion_stats,
            action_stats=action_stats
        )
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {str(e)}")
        return render_template('error.html', error=str(e))

@admin_bp.route('/admin/rules', methods=['GET'])
def get_rules():
    """API endpoint to get all rules"""
    try:
        rules = rules_loader.get_rules()
        return jsonify({
            'success': True,
            'rules': rules
        })
    except Exception as e:
        logger.error(f"Error getting rules: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/admin/rules/<rule_id>', methods=['GET'])
def get_rule(rule_id):
    """API endpoint to get a specific rule"""
    try:
        rule = rules_loader.get_rule_by_id(rule_id)
        if rule:
            return jsonify({
                'success': True,
                'rule': rule
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Rule not found: {rule_id}'
            }), 404
    except Exception as e:
        logger.error(f"Error getting rule: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/admin/rules', methods=['POST'])
def add_rule():
    """API endpoint to add a new rule"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        success = rules_loader.add_rule(data)
        if success:
            return jsonify({
                'success': True,
                'message': 'Rule added successfully',
                'rule': data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add rule'
            }), 400
    except Exception as e:
        logger.error(f"Error adding rule: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/admin/rules/<rule_id>', methods=['PUT'])
def update_rule(rule_id):
    """API endpoint to update a rule"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        success = rules_loader.update_rule(rule_id, data)
        if success:
            updated_rule = rules_loader.get_rule_by_id(rule_id)
            return jsonify({
                'success': True,
                'message': 'Rule updated successfully',
                'rule': updated_rule
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to update rule: {rule_id}'
            }), 404
    except Exception as e:
        logger.error(f"Error updating rule: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/admin/rules/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """API endpoint to delete a rule"""
    try:
        success = rules_loader.delete_rule(rule_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Rule deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to delete rule: {rule_id}'
            }), 404
    except Exception as e:
        logger.error(f"Error deleting rule: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/admin/logs', methods=['GET'])
def get_logs():
    """API endpoint to get interaction logs"""
    try:
        limit = request.args.get('limit', 100, type=int)
        logs = get_recent_interactions(limit=limit)
        return jsonify({
            'success': True,
            'logs': logs
        })
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/admin/logs', methods=['DELETE'])
def delete_logs():
    """API endpoint to clear logs"""
    try:
        success = clear_logs()
        if success:
            return jsonify({
                'success': True,
                'message': 'Logs cleared successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to clear logs'
            }), 400
    except Exception as e:
        logger.error(f"Error clearing logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/admin/stats/emotions', methods=['GET'])
def get_emotion_stats():
    """API endpoint to get emotion statistics"""
    try:
        stats = get_emotion_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting emotion statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/admin/stats/actions', methods=['GET'])
def get_action_stats():
    """API endpoint to get action statistics"""
    try:
        stats = get_action_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting action statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/admin/memories/<user_id>', methods=['GET'])
def get_user_memories(user_id):
    """API endpoint to get all memories for a user"""
    try:
        memories = get_all_user_memories(user_id)
        return jsonify({
            'success': True,
            'user_id': user_id,
            'memories': memories
        })
    except Exception as e:
        logger.error(f"Error getting user memories: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/admin/stats', methods=['GET'])
def admin_stats():
    """
    Advanced analytics dashboard
    Shows extended statistics and user analytics
    """
    try:
        # Get date range from request parameters
        today = datetime.datetime.now().date()
        default_start = (today - datetime.timedelta(days=30)).isoformat()
        default_end = today.isoformat()
        
        start_date = request.args.get('start', default_start)
        end_date = request.args.get('end', default_end)
        
        # Get statistics
        emotion_stats = get_emotion_statistics()
        action_stats = get_action_statistics()
        daily_usage = get_daily_usage(start_date, end_date)
        language_stats = get_language_statistics()
        rule_stats = get_rule_effectiveness()
        
        # Get general metrics
        total_interactions = sum(emotion_stats.values())
        unique_users = get_unique_users_count()
        active_today = get_active_users_today()
        avg_response_time = get_average_response_time()
        
        # Get recent logs with language information
        recent_logs = get_recent_interactions(limit=20)
        
        return render_template(
            'admin_stats.html',
            emotion_stats=emotion_stats,
            action_stats=action_stats,
            daily_usage=daily_usage,
            language_stats=language_stats,
            rule_stats=rule_stats,
            recent_logs=recent_logs,
            total_interactions=total_interactions,
            total_users=unique_users,
            active_today=active_today,
            avg_response_time=avg_response_time,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"Error loading analytics dashboard: {str(e)}")
        return render_template('error.html', error=str(e))

def get_daily_usage(start_date, end_date):
    """
    Get daily usage statistics within a date range
    Returns a list of {date, count} dictionaries
    """
    try:
        # This is a placeholder implementation
        # In a real system, this would query the database for daily counts
        # between the given dates
        
        # Parse dates
        try:
            start = datetime.datetime.fromisoformat(start_date).date()
            end = datetime.datetime.fromisoformat(end_date).date()
        except ValueError:
            today = datetime.datetime.now().date()
            start = today - datetime.timedelta(days=30)
            end = today
        
        # Generate a list of dates between start and end
        date_range = []
        current = start
        while current <= end:
            date_range.append(current.isoformat())
            current += datetime.timedelta(days=1)
        
        # Get logs and count by date
        logs = get_recent_interactions(limit=1000)  # Assuming this is from imported log_manager
        
        # Create a dictionary to count interactions by date
        counts_by_date = {date: 0 for date in date_range}
        
        # Count interactions by date
        for log in logs:
            try:
                # Convert timestamp to date only
                log_datetime = datetime.datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S')
                log_date = log_datetime.date().isoformat()
                
                # If the date is in our range, increment the count
                if log_date in counts_by_date:
                    counts_by_date[log_date] += 1
            except (ValueError, KeyError):
                # Skip logs with invalid timestamps
                continue
        
        # Convert the dictionary to a list of {date, count} objects
        result = [{'date': date, 'count': counts_by_date[date]} for date in date_range]
        
        return result
    except Exception as e:
        logger.error(f"Error getting daily usage statistics: {str(e)}")
        return []

def get_language_statistics():
    """
    Get statistics on language usage in interactions
    Returns a dictionary mapping language codes to counts
    """
    try:
        # Get logs
        logs = get_recent_interactions(limit=1000)
        
        # Count interactions by language
        language_counts = {'en': 0, 'ar': 0}
        
        for log in logs:
            lang = log.get('language', 'en')
            if lang in language_counts:
                language_counts[lang] += 1
        
        return language_counts
    except Exception as e:
        logger.error(f"Error getting language statistics: {str(e)}")
        return {'en': 0, 'ar': 0}

def get_rule_effectiveness():
    """
    Calculate effectiveness scores for each rule
    Returns a list of {id, effectiveness} dictionaries
    """
    try:
        # Get rules
        rules = rules_loader.get_rules()
        
        # This is a simplified implementation
        # In a real system, you would calculate effectiveness based on
        # user feedback, conversation continuations, etc.
        
        # For now, we'll simulate effectiveness based on rule weights
        effectiveness = []
        
        for rule in rules:
            # Convert weight (typically 0.1 to 2.0) to a percentage (0 to 100)
            # Higher weights indicate better performing rules
            weight = float(rule.get('weight', 1.0))
            score = min(100, max(0, (weight - 0.5) * 50))  # Convert to 0-100 scale
            
            effectiveness.append({
                'id': rule.get('id', 'unknown'),
                'effectiveness': score
            })
        
        return effectiveness
    except Exception as e:
        logger.error(f"Error calculating rule effectiveness: {str(e)}")
        return []

def get_unique_users_count():
    """
    Get count of unique users who have interacted with the system
    """
    try:
        # Get logs
        logs = get_recent_interactions(limit=1000)
        
        # Extract unique user IDs
        user_ids = set()
        for log in logs:
            user_id = log.get('user_id')
            if user_id:
                user_ids.add(user_id)
        
        return len(user_ids)
    except Exception as e:
        logger.error(f"Error getting unique users count: {str(e)}")
        return 0

def get_active_users_today():
    """
    Get count of users active today
    """
    try:
        # Get logs
        logs = get_recent_interactions(limit=1000)
        
        # Get today's date
        today = datetime.datetime.now().date().isoformat()
        
        # Extract unique user IDs from today's logs
        user_ids = set()
        for log in logs:
            try:
                # Convert timestamp to date only
                log_datetime = datetime.datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S')
                log_date = log_datetime.date().isoformat()
                
                # If the log is from today, add the user ID
                if log_date == today and log.get('user_id'):
                    user_ids.add(log.get('user_id'))
            except (ValueError, KeyError):
                # Skip logs with invalid timestamps
                continue
        
        return len(user_ids)
    except Exception as e:
        logger.error(f"Error getting active users count: {str(e)}")
        return 0

def get_average_response_time():
    """
    Calculate average response time in milliseconds
    """
    try:
        # This would typically use data from a performance monitoring table
        # For now, we'll return a simulated value
        # In a production system, you would track the time between receiving
        # a request and sending a response
        return 230.5  # milliseconds
    except Exception as e:
        logger.error(f"Error calculating average response time: {str(e)}")
        return 0