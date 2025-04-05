"""
Enhanced CORS Support Module for Flask Applications

This module provides utility functions to add comprehensive CORS headers
to Flask applications, making them accessible for external services like
the Replit web application feedback tool.
"""

from flask import Blueprint, jsonify, current_app

def create_cors_blueprint():
    """Create a Flask blueprint with routes specifically designed for CORS testing"""
    cors_blueprint = Blueprint('cors', __name__)
    
    @cors_blueprint.route('/cors-test')
    def cors_test():
        """Test endpoint for CORS configuration"""
        response = jsonify({
            "status": "ok",
            "message": "CORS test endpoint is working",
            "cors_enabled": True,
            "timestamp": "2025-04-05T18:00:00Z"
        })
        
        # Add comprehensive CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        
        return response
    
    @cors_blueprint.route('/cors-test', methods=['OPTIONS'])
    def cors_test_options():
        """Handle OPTIONS requests for CORS preflight"""
        response = jsonify({})
        
        # Add comprehensive CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        
        return response
    
    return cors_blueprint

def add_cors_headers_after_request(response):
    """Add CORS headers to all responses from this Flask application"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

def enhance_cors(app):
    """Enhance a Flask application with comprehensive CORS support"""
    # Register after_request handler to add CORS headers to all responses
    app.after_request(add_cors_headers_after_request)
    
    # Handle OPTIONS requests globally
    @app.route('/', methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path=None):
        """Handle OPTIONS requests for CORS preflight"""
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    
    # Register the CORS blueprint
    cors_blueprint = create_cors_blueprint()
    app.register_blueprint(cors_blueprint)
    
    return app