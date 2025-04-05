"""
Health check module for Replit compatibility
"""

from flask import Blueprint, jsonify, Response

# Create blueprint for health check endpoints
health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health():
    """Primary health check endpoint for Replit web application feedback tool"""
    return Response('{"status":"ok"}', mimetype='application/json')

@health_bp.route('/replit-health')
def replit_health():
    """Secondary health check endpoint"""
    return Response('{"status":"ok"}', mimetype='application/json')

@health_bp.route('/replit-feedback-health')
def replit_feedback_health():
    """Alternative health check specifically for Replit feedback tool"""
    return Response('{"status":"ok","message":"Server is running"}', mimetype='application/json')

def init_health_routes(app):
    """Initialize health check routes on the given Flask app"""
    app.register_blueprint(health_bp)