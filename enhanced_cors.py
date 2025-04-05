"""
Enhanced CORS Configuration for Replit Web Application Feedback Tool

This module provides advanced CORS configuration specifically designed
to work with the Replit web application feedback tool.
"""

import logging
import re
from flask import Flask, request, Response
from flask_cors import CORS

logger = logging.getLogger(__name__)

def configure_cors(app, dev_mode=False):
    """
    Configure enhanced CORS settings for the Replit feedback tool
    
    Args:
        app: Flask application instance
        dev_mode: Enable development mode with additional origins
    """
    # Create a list of allowed origins that includes all Replit domains
    allowed_origins = [
        # Original domains
        'https://mashaaer.replit.app',
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        # Replit-specific domains
        'https://*.replit.app',
        'https://replit.com',
        # Wildcard for development
        '*'
    ]
    
    logger.info(f"Configuring enhanced CORS with origins: {allowed_origins}")
    
    # Initialize CORS with permissive settings
    CORS(app, 
         resources={r"/*": {"origins": allowed_origins}},
         supports_credentials=False,
         methods=["GET", "POST", "OPTIONS", "HEAD"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"])
    
    # Add custom CORS headers for all responses
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin', '*')
        
        # Log origin information for debugging
        logger.debug(f"Request Origin: {origin}")
        
        # Set CORS headers with dynamic origin
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'  # Cache preflight request for 1 hour
        
        # Log the response headers for debugging
        logger.debug(f"Response headers: {dict(response.headers)}")
        
        return response
    
    # Handle OPTIONS requests explicitly
    @app.route('/', methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path=''):
        """Handle OPTIONS preflight requests"""
        origin = request.headers.get('Origin', '*')
        logger.debug(f"OPTIONS request from origin: {origin} for path: {path}")
        
        response = Response('')
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        
        return response
    
    # Return the CORS instance
    return CORS