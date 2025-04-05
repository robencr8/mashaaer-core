"""
Feedback Tool Routes for Mashaaer Feelings

This module initializes the routes specifically required for the 
Replit web application feedback tool to work correctly.
"""

import logging
import os
from datetime import datetime
from flask import jsonify, make_response, render_template, send_from_directory, Response

logger = logging.getLogger(__name__)

def init_feedback_tool_routes(app):
    """Initialize routes needed for the Replit feedback tool to work properly"""
    logger.info("Feedback tool routes initialized")
    
    @app.route('/')
    def root_route():
        """Root route with enhanced CORS headers to ensure Replit tools work properly"""
        logger.info("Root route accessed, serving welcome page with CORS headers")
        
        # Simple HTML response that works well with web application feedback tool
        html = """<!DOCTYPE html>
<html>
<head>
  <title>Mashaaer Feelings</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
  <h1>Mashaaer Feelings API</h1>
  <p>Welcome! The API is running.</p>
  <p><a href="/cosmic-onboarding">Access the Cosmic Onboarding Experience</a></p>
</body>
</html>"""
        
        response = Response(html, mimetype='text/html')
        
        # Add explicit CORS headers for maximum compatibility
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        
        return response
    
    @app.route('/', methods=['OPTIONS'])
    def root_options():
        """Handle OPTIONS requests for CORS preflight at the root path"""
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    
    return app