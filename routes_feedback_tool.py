"""
Feedback Tool Routes for Mashaaer Feelings

This module initializes the routes specifically required for the 
Replit web application feedback tool to work correctly.
"""

import logging
import os
from datetime import datetime
from flask import jsonify, make_response, render_template, send_from_directory

logger = logging.getLogger(__name__)

def init_feedback_tool_routes(app):
    """Initialize routes needed for the Replit feedback tool to work properly"""
    logger.info("Feedback tool routes initialized")
    
    @app.route('/')
    def root_route():
        """Root route with enhanced CORS headers to ensure Replit tools work properly"""
        logger.info("Root route accessed, serving welcome page with CORS headers")
        response = make_response("Mashaaer Feelings API - Welcome! The API is running. Access /cosmic-onboarding for the app.")
        
        # Add explicit CORS headers for maximum compatibility
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        
        return response
    
    return app