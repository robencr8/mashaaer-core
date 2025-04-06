"""
CORS Debugging and Configuration Utility

This module provides tools to diagnose and fix CORS issues with the Replit feedback tool.
"""
import os
import logging
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_cors_request(request):
    """Log detailed information about a request for CORS debugging purposes"""
    logger.debug("==== CORS Debug Request Information ====")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request path: {request.path}")
    logger.debug(f"Request origin: {request.headers.get('Origin', 'Not provided')}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    logger.debug("=======================================")

def apply_cors_headers(response, allowed_origins=None):
    """
    Apply proper CORS headers to a response
    
    Args:
        response: The Flask response object
        allowed_origins: List of allowed origins or None to use '*'
    """
    # Get origin from request
    origin = request.headers.get('Origin', '')
    
    # If allowed_origins is provided and not empty
    if allowed_origins:
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
        elif '*' in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = '*'
    else:
        # Default to allow all origins
        response.headers['Access-Control-Allow-Origin'] = '*'
    
    # Add remaining CORS headers
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    logger.debug(f"Applied CORS headers: {dict(response.headers)}")
    return response

def configure_cors_for_replit(app):
    """
    Configure CORS specifically for Replit feedback tool
    
    Args:
        app: Flask application instance
    """
    # Known Replit origins
    replit_origins = [
        'https://replit.com',
        'https://*.replit.app',
        'https://*.repl.co',
        '*.repl.co',
        'replit.com',
        '*.replit.app',
        '*',  # Allow all origins as fallback
    ]
    
    # Add feedback tool origin from environment variable if available
    feedback_tool_origin = os.environ.get('FEEDBACK_TOOL_ORIGIN')
    if feedback_tool_origin:
        replit_origins.append(feedback_tool_origin)
        logger.info(f"Added FEEDBACK_TOOL_ORIGIN to allowed origins: {feedback_tool_origin}")
    
    # Register CORS debugging endpoint
    @app.route('/api/cors-debug', methods=['GET', 'OPTIONS'])
    def cors_debug_endpoint():
        """Endpoint that returns CORS debugging information"""
        debug_cors_request(request)
        
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
        else:
            data = {
                'status': 'ok',
                'message': 'CORS debug endpoint',
                'request': {
                    'method': request.method,
                    'path': request.path,
                    'origin': request.headers.get('Origin', 'Not provided'),
                    'headers': dict(request.headers),
                }
            }
            response = jsonify(data)
        
        return apply_cors_headers(response, replit_origins)
    
    # Add after_request handler to add CORS headers to all responses
    @app.after_request
    def add_cors_headers(response):
        """Add CORS headers to all responses"""
        # Log request information for debugging
        debug_cors_request(request)
        
        # Add CORS headers
        return apply_cors_headers(response, replit_origins)
    
    # Add global OPTIONS handler
    @app.route('/', methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options(path=None):
        """Handle OPTIONS requests for CORS preflight"""
        debug_cors_request(request)
        response = app.make_default_options_response()
        return apply_cors_headers(response, replit_origins)
    
    return app

def add_minimal_test_endpoint(app):
    """
    Add a minimal test endpoint for CORS testing
    
    Args:
        app: Flask application instance
    """
    @app.route('/api/minimal', methods=['GET', 'OPTIONS'])
    def minimal_test():
        """Minimal test endpoint for CORS testing"""
        debug_cors_request(request)
        
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
        else:
            data = {
                'status': 'ok',
                'message': 'Minimal test endpoint',
                'cors_enabled': True,
            }
            response = jsonify(data)
        
        # Log origins for debugging
        logger.debug(f"Request origin: {request.headers.get('Origin', 'Not provided')}")
        
        # Add CORS headers
        origin = request.headers.get('Origin', '')
        response.headers['Access-Control-Allow-Origin'] = origin or '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response
    
    return app