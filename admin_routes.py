"""
Admin Routes for Mashaaer Feelings Application
Provides admin dashboard and management features
"""
from flask import Blueprint, render_template, request, jsonify, current_app
import logging
import json
import os
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