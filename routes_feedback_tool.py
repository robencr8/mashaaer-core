"""
Specialized routes for web application feedback tool.
These routes are specifically designed for maximum compatibility with the Replit
feedback tool.
"""

import logging
import os
from datetime import datetime
from flask import request, jsonify, make_response

# Set up logging
logger = logging.getLogger(__name__)

def init_feedback_tool_routes(app):
    """
    Initialize routes specifically optimized for the web application feedback tool.
    
    Args:
        app: Flask application instance
    """
    logger.info("Feedback tool routes initialized")
    
    @app.route('/feedback-tool-endpoint', methods=['GET', 'POST', 'OPTIONS'])
    def feedback_tool_endpoint():
        """Endpoint optimized for the web application feedback tool with all CORS headers"""
        # Get the actual origin from the request
        origin = request.headers.get('Origin', '*')
        
        # Log request details for debugging
        logger.info(f"Feedback tool endpoint accessed via {request.method} from {origin}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        # For OPTIONS preflight requests
        if request.method == 'OPTIONS':
            logger.info(f"Handling OPTIONS preflight request from {origin}")
            response = make_response()
            
            # Add CORS headers (echo back the exact requesting origin)
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
            response.headers['Access-Control-Max-Age'] = '3600'
            
            return response
        
        # For GET requests - return basic status info
        elif request.method == 'GET':
            response_data = {
                'status': 'online',
                'message': 'Mashaaer Feelings API is online and accessible',
                'service': 'Feedback Tool Compatibility Endpoint',
                'timestamp': datetime.now().isoformat()
            }
            
            response = jsonify(response_data)
        
        # For POST requests - echo back the data with a success message
        elif request.method == 'POST':
            try:
                # Try to get JSON data if available
                if request.is_json:
                    data = request.get_json()
                    logger.debug(f"Received JSON data: {data}")
                    
                    response_data = {
                        'status': 'success',
                        'message': 'Data received successfully',
                        'received_data': data,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    # Handle form data or other content types
                    logger.debug(f"Received non-JSON data with content type: {request.content_type}")
                    
                    response_data = {
                        'status': 'success',
                        'message': 'Request received successfully',
                        'content_type': request.content_type,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Add form data if present
                    if request.form:
                        response_data['form_data'] = dict(request.form)
                
                response = jsonify(response_data)
                
            except Exception as e:
                logger.error(f"Error processing POST request: {str(e)}")
                response = jsonify({
                    'status': 'error',
                    'message': f'Error processing request: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Set CORS headers for all response types
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
        
        return response
        
    @app.route('/api/health', methods=['GET', 'OPTIONS'])
    def health_check():
        """Ultra minimal health check endpoint with maximum CORS headers"""
        # Get the actual origin from the request
        origin = request.headers.get('Origin', '*')
        
        # For OPTIONS preflight requests
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = '*'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response
            
        # Simple health check response
        response = make_response('OK')
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Access-Control-Allow-Origin'] = origin
        
        return response
        
    @app.route('/', methods=['GET', 'OPTIONS'])
    def root_health_check():
        """Ultra minimal health check at the root endpoint with maximum CORS headers"""
        # Get the actual origin from the request
        origin = request.headers.get('Origin', '*')
        
        # For OPTIONS preflight requests
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = '*'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response
            
        # Simple text response for maximum compatibility
        response = make_response('Mashaaer Feelings API is running')
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Access-Control-Allow-Origin'] = origin
        
        return response