"""
Routes specifically designed for feedback tool compatibility.

These routes provide endpoints optimized for the web application feedback tool
with enhanced CORS support and diagnostic information.
"""

from flask import Blueprint, request, jsonify, make_response, render_template, current_app
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

feedback_tool_bp = Blueprint('feedback_tool', __name__)

@feedback_tool_bp.route('/feedback-tool-guide')
def feedback_tool_guide():
    """Serve the feedback tool integration guide HTML page"""
    return current_app.send_static_file('feedback_tool_guide.html')

@feedback_tool_bp.route('/api/feedback-tool-status')
def feedback_tool_status():
    """Status endpoint optimized for feedback tool with explicit CORS headers"""
    origin = request.headers.get('Origin', '*')
    logger.info(f"Feedback tool status endpoint accessed from origin: {origin}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    # Create response with extra diagnostic information
    response = jsonify({
        'status': 'online',
        'message': 'Server is accessible by the feedback tool',
        'timestamp': datetime.now().isoformat(),
        'request': {
            'headers': {k: v for k, v in request.headers.items()},
            'origin': origin,
            'method': request.method,
            'remote_addr': request.remote_addr
        },
        'replit_info': {
            'domain': os.environ.get('REPL_SLUG', 'unknown') + '.' + os.environ.get('REPL_OWNER', 'unknown') + '.repl.co',
            'id': os.environ.get('REPL_ID', 'unknown'),
            'slug': os.environ.get('REPL_SLUG', 'unknown')
        }
    })
    
    # Add explicit CORS headers
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Content-Length'
    
    return response

@feedback_tool_bp.route('/api/feedback-tool-ping')
def feedback_tool_ping():
    """Ultra-minimal ping endpoint for feedback tool with plain text response"""
    origin = request.headers.get('Origin', '*')
    logger.info(f"Feedback tool ping endpoint accessed from origin: {origin}")
    
    # Create simple text response
    response = make_response("PONG - Server is accessible by the feedback tool")
    response.headers['Content-Type'] = 'text/plain'
    
    # Add explicit CORS headers
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    
    return response

def init_feedback_tool_routes(app):
    """Initialize feedback tool routes with the Flask app"""
    app.register_blueprint(feedback_tool_bp)
    logger.info("Feedback tool routes initialized")
    
    # Create a route at the app level for maximum compatibility
    @app.route('/feedback')
    def feedback_redirect():
        """Redirect to the feedback tool guide"""
        return app.send_static_file('feedback_tool_guide.html')
