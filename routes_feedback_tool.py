"""
Routes specifically designed for feedback tool compatibility.

These routes provide endpoints optimized for the web application feedback tool
with enhanced CORS support and diagnostic information.
"""
import os
import logging
import json
from datetime import datetime
from flask import Blueprint, request, make_response, jsonify, send_from_directory

logger = logging.getLogger(__name__)

FEEDBACK_TOOL_ORIGIN = os.environ.get('FEEDBACK_TOOL_ORIGIN', None)

feedback_tool_bp = Blueprint('feedback_tool', __name__)

@feedback_tool_bp.route('/feedback-tool-guide')
def feedback_tool_guide():
    """Serve the feedback tool integration guide HTML page"""
    return send_from_directory('static', 'feedback_tool_guide.html')

@feedback_tool_bp.route('/feedback-tool-status')
def feedback_tool_status():
    """Status endpoint optimized for feedback tool with explicit CORS headers and request details."""
    # Get the origin from the request headers or use configured origin as fallback
    origin = request.headers.get('Origin', FEEDBACK_TOOL_ORIGIN or '*')
    logger.info(f"Feedback tool status endpoint accessed from origin: {origin}")
    
    # Log detailed request information
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request remote address: {request.remote_addr}")
    
    # For OPTIONS requests (preflight)
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight request for feedback tool status")
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response
    
    # Create response with detailed diagnostic information
    status_info = {
        'message': 'Server is running and configured for feedback tool compatibility',
        'timestamp': datetime.now().isoformat(),
        'cors_config': {
            'feedback_tool_origin': FEEDBACK_TOOL_ORIGIN,
            'request_origin': origin,
            'access_control_origin': origin if origin != '*' else '*'
        },
        'request_info': {
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'host': request.host,
            'user_agent': request.user_agent.string,
            'headers': {k: v for k, v in request.headers.items()}
        }
    }
    
    # Create JSON response
    response = make_response(jsonify(status_info))
    
    # Add explicit CORS headers to ensure compatibility with feedback tool
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Content-Length, Date'
    
    return response

@feedback_tool_bp.route('/feedback-tool-ping')
def feedback_tool_ping():
    """Ultra-minimal ping endpoint for feedback tool with plain text response"""
    # Get the origin from the request headers or use configured origin as fallback
    origin = request.headers.get('Origin', FEEDBACK_TOOL_ORIGIN or '*')
    
    # For OPTIONS requests (preflight)
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    
    # Create minimal response
    response = make_response("PONG")
    response.headers['Content-Type'] = 'text/plain'
    
    # Add explicit CORS headers
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    
    return response

def init_feedback_tool_routes(app):
    """Initialize feedback tool routes with the Flask app"""
    app.register_blueprint(feedback_tool_bp, url_prefix='/api')
    
    @app.route('/feedback-tool-redirect')
    def feedback_redirect():
        """Redirect to the feedback tool guide"""
        return app.redirect('/api/feedback-tool-guide')
    
    logger.info("Feedback tool routes initialized")
    return feedback_tool_bp