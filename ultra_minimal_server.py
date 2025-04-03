"""
Ultra-minimal Flask server specifically for CORS testing
This is a standalone server that can be run independently of the main application
"""

import logging
from datetime import datetime

from flask import Flask, jsonify, request

# Create a minimal Flask app
app = Flask(__name__)

# Configure basic logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Root route serves a simple text response
@app.route('/')
def index():
    """Root route that returns a simple text response"""
    logger.info(f"Received request to / from {request.headers.get('Origin', 'unknown origin')}")
    response = jsonify({
        'message': 'Ultra minimal server is running',
        'timestamp': datetime.now().isoformat()
    })
    
    # Explicitly add CORS headers to ensure maximum compatibility
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    
    return response

# Specific test endpoint for the feedback tool
@app.route('/api/test-cors', methods=['GET', 'POST', 'OPTIONS'])
def test_cors_endpoint():
    """Test endpoint specifically for CORS testing with the feedback tool"""
    logger.info(f"Received {request.method} request to /api/test-cors from {request.headers.get('Origin', 'unknown origin')}")
    
    # For OPTIONS requests (preflight)
    if request.method == 'OPTIONS':
        logger.info("Handling OPTIONS preflight request")
        response = jsonify({'message': 'Preflight request successful'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response
    
    # For GET or POST requests
    response = jsonify({
        'message': 'CORS test successful',
        'method': request.method,
        'origin': request.headers.get('Origin', 'unknown'),
        'timestamp': datetime.now().isoformat()
    })
    
    # Explicitly set CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    
    return response

@app.route('/diagnostic', methods=['GET'])
def diagnostic():
    """Diagnostic endpoint to show request information"""
    logger.info(f"Received request to /diagnostic from {request.headers.get('Origin', 'unknown origin')}")
    
    # Gather request information
    request_info = {
        'method': request.method,
        'url': request.url,
        'headers': {k: v for k, v in request.headers.items()},
        'remote_addr': request.remote_addr,
        'timestamp': datetime.now().isoformat()
    }
    
    response = jsonify(request_info)
    
    # Explicitly set CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    
    return response

if __name__ == '__main__':
    # Run the ultra-minimal server
    logger.info("Starting ultra-minimal CORS testing server")
    app.run(host='0.0.0.0', port=5000, debug=True)