"""
Ultra-minimal Flask server specifically for CORS testing
This is a standalone server that can be run independently of the main application
"""
import logging
import json
from datetime import datetime
from flask import Flask, jsonify, request, make_response

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ultra-minimal-server")

app = Flask(__name__)

@app.route('/')
def index():
    """Root route that returns a simple text response"""
    origin = request.headers.get('Origin', '*')
    logger.info(f"Root route accessed from origin: {origin}")
    
    response = make_response("Ultra-minimal server is running. Server time: " + 
                             datetime.now().isoformat())
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    
    return response

@app.route('/api/test-cors-endpoint', methods=['GET', 'POST', 'OPTIONS'])
def test_cors_endpoint():
    """Test endpoint specifically for CORS testing with the feedback tool"""
    # Get the origin from the request headers or use wildcard as fallback
    origin = request.headers.get('Origin', '*')
    logger.info(f"Received {request.method} request to /api/test-cors-endpoint from {origin}")
    
    # For OPTIONS requests (preflight)
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight request from {origin}")
        response = make_response()
        # Explicitly set CORS headers - echo back the origin instead of using wildcard
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response
    
    # For GET or POST requests
    response_data = {
        'message': 'CORS test successful',
        'method': request.method,
        'origin': origin,
        'timestamp': datetime.now().isoformat(),
        'headers_received': {k: v for k, v in request.headers.items()},
    }
    
    logger.info(f"Response data: {json.dumps(response_data, default=str)}")
    
    response = jsonify(response_data)
    
    # Explicitly set CORS headers - echo back the origin instead of using wildcard
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    
    return response

@app.route('/api/diagnostic', methods=['GET', 'POST', 'OPTIONS'])
def diagnostic():
    """Diagnostic endpoint to show request information"""
    # Get the origin from the request headers or use wildcard as fallback
    origin = request.headers.get('Origin', '*')
    logger.info(f"Diagnostic endpoint accessed from origin: {origin}")
    
    # For OPTIONS requests (preflight)
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight request from {origin}")
        response = make_response()
        # Explicitly set CORS headers - echo back the origin instead of using wildcard
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response
    
    # Prepare detailed diagnostic information
    headers = dict(request.headers)
    response_data = {
        'message': 'Diagnostic information',
        'method': request.method,
        'url': request.url,
        'path': request.path,
        'origin': origin,
        'headers': headers,
        'remote_addr': request.remote_addr,
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"Diagnostic data: {json.dumps(response_data, default=str)}")
    
    response = jsonify(response_data)
    
    # Explicitly set CORS headers - echo back the origin instead of using wildcard
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    
    return response

if __name__ == '__main__':
    logger.info("Starting ultra-minimal server on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)