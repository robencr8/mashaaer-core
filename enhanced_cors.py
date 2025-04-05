"""
Enhanced CORS Configuration for Replit Web Application Feedback Tool

This module provides advanced CORS configuration specifically designed
to work with the Replit web application feedback tool.
"""

from flask import Flask, request, Response
from flask_cors import CORS

def configure_cors(app):
    """
    Configure enhanced CORS settings for the Replit feedback tool
    
    Args:
        app: Flask application instance
    """
    # Initialize CORS with very permissive settings
    CORS(app, 
         resources={r"/*": {"origins": "*"}},
         supports_credentials=False,
         methods=["GET", "POST", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"])
    
    # Add custom CORS headers for all responses
    @app.after_request
    def add_cors_headers(response):
        # These headers are belt-and-suspenders in addition to flask-cors
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'  # Cache preflight request for 1 hour
        return response
    
    # Handle OPTIONS requests explicitly
    @app.route('/', methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path=''):
        """Handle OPTIONS preflight requests"""
        response = Response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response