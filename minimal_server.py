"""
Ultra-minimal Flask server for testing web application feedback tool
This uses the absolute minimum functionality to serve content with appropriate CORS headers
"""

import logging
from datetime import datetime

from flask import Flask, make_response, jsonify

# Create a minimal Flask app
app = Flask(__name__)

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Setup CORS headers for all responses
@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

# Root route serves a simple text response
@app.route('/')
def index():
    """Root route that returns a simple text response"""
    response = make_response("Minimal server is running. Status: OK. Timestamp: " + 
                           datetime.now().isoformat())
    response.headers['Content-Type'] = 'text/plain'
    return response

# Test route returns JSON
@app.route('/test')
def test():
    """Test route that returns JSON"""
    return jsonify({
        'status': 'success',
        'message': 'Minimal server is reachable',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Run the minimal server
    app.run(host='0.0.0.0', port=5000, debug=True)