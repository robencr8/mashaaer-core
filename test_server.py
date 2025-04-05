"""
Simple test server for verifying Replit web application feedback tool compatibility.
This is a standalone server that doesn't depend on other components.
"""

from flask import Flask, jsonify, make_response
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Root route returning a simple text response"""
    response = make_response("Test Server is Running - Replit Compatibility Test")
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

@app.route('/test')
def test():
    """Test endpoint with CORS headers"""
    response = make_response("Test endpoint is working")
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

@app.route('/api/health')
def health():
    """Health check endpoint"""
    response = make_response(jsonify({'status': 'ok', 'message': 'Test server is running'}))
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

# Allow cross-domain OPTIONS requests
@app.route('/', methods=['OPTIONS'])
@app.route('/test', methods=['OPTIONS'])
@app.route('/api/health', methods=['OPTIONS'])
def options_handler():
    """Handle OPTIONS requests for CORS preflight"""
    response = make_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)