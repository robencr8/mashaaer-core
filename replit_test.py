"""
Replit Compatibility Test Script

This script provides a simple Flask application that confirms
the accessibility of the main application from the Replit environment.
Run this separately if you're having issues with the main application
in the web application feedback tool.
"""

import os
from flask import Flask, jsonify, make_response

app = Flask(__name__)

@app.route('/')
def index():
    """Root route returning a simple text response"""
    response = make_response("Mashaaer Replit Test is running")
    # Add CORS headers for Replit compatibility
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/status')
def status():
    """Status endpoint returning JSON"""
    return jsonify({
        'status': 'online',
        'app': 'Mashaaer Replit Test',
        'environment': 'Replit'
    })

if __name__ == "__main__":
    port = 5000
    # Check if port 5000 is specified in an environment variable
    if 'PORT' in os.environ:
        port = int(os.environ['PORT'])
        
    print(f"Starting Replit test server on port {port}")
    app.run(host='0.0.0.0', port=port)