"""
Ultra-minimal standalone Flask server for web application feedback tool
This is a dedicated server that runs on a different port (5001)
"""
import os
import logging
from flask import Flask, request, jsonify, make_response

# Configure basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a minimal Flask app
app = Flask(__name__)

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses - maximally permissive for testing"""
    logger.debug(f"Adding CORS headers to response")
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Max-Age'] = '3600'
    logger.debug(f"Response headers: {dict(response.headers)}")
    return response

@app.route('/')
def index():
    """Root route that returns a simple text response"""
    logger.info(f"Request to /: {request.method} from {request.remote_addr}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    
    return "Standalone minimal server is running. This is a plain text response."

@app.route('/test')
def test():
    """Test route that returns JSON"""
    logger.info(f"Request to /test: {request.method} from {request.remote_addr}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    
    return jsonify({
        'status': 'success',
        'message': 'Standalone minimal server is reachable',
        'timestamp': 'test-timestamp'
    })

@app.route('/ping')
def ping():
    """Simple ping endpoint with plain text response"""
    logger.info(f"Request to /ping: {request.method} from {request.remote_addr}")
    return make_response("pong")

@app.route('/status')
def status():
    """Status endpoint with JSON response"""
    logger.info(f"Request to /status: {request.method} from {request.remote_addr}")
    return jsonify({
        'status': 'operational',
        'service': 'standalone-minimal-server',
        'uptime': '1m'
    })

if __name__ == '__main__':
    # Run on port 5001 to avoid conflict with main application
    port = int(os.environ.get('PORT_MINIMAL', 5001))
    logger.info(f"Starting standalone minimal server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)