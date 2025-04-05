"""
Feedback Tool Routes for Mashaaer Feelings

This module initializes the routes specifically required for the 
Replit web application feedback tool to work correctly.
"""

import logging
import os
from datetime import datetime
from flask import jsonify, make_response, render_template, send_from_directory, Response, request

logger = logging.getLogger(__name__)

def init_feedback_tool_routes(app):
    """Initialize routes needed for the Replit feedback tool to work properly"""
    logger.info("Feedback tool routes initialized")
    
    @app.route('/')
    def root_route():
        """Ultra-simple root route with minimal HTML specifically designed for the Replit feedback tool"""
        logger.info(f"Root route accessed: {request.method}, headers: {dict(request.headers)}")
        
        # Extremely simple HTML document with no dependencies
        html = """<!DOCTYPE html>
<html>
<head>
  <title>Mashaaer Feelings</title>
  <meta charset="UTF-8">
</head>
<body>
  <h1>Welcome to Mashaaer Feelings</h1>
  <p>The application is running correctly.</p>
  <p><a href="/cosmic-onboarding">Start Cosmic Onboarding</a></p>
</body>
</html>"""
        
        response = Response(html, mimetype='text/html')
        
        # Add all possible CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
        
        return response
    
    @app.route('/', methods=['OPTIONS'])
    def root_options():
        """Handle OPTIONS requests for CORS preflight at the root path"""
        logger.info(f"OPTIONS request at root: headers: {dict(request.headers)}")
        
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
        return response
    
    @app.route('/health')
    def health_check():
        """Simple health check endpoint specifically for Replit compatibility"""
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
        
    return app