#!/usr/bin/env python3
"""
Standalone minimal Flask server for testing the web application feedback tool

This is a completely standalone minimal server that runs on port 3000 and doesn't
require any of the dependencies of the main project. It can be used to isolate whether
the issue is with the main application or with the web application feedback tool.
"""

import os
import logging
from datetime import datetime
import json

from flask import Flask, make_response, request, jsonify

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses"""
    origin = request.headers.get('Origin', '*')
    
    # Log the origin for debugging
    logger.info(f"Request from origin: {origin}")
    
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    
    return response

@app.route('/')
def index():
    """Root endpoint - returns a simple text response"""
    logger.info("Root endpoint accessed")
    response = make_response("Standalone Minimal Server is running!")
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    response = make_response("OK")
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/api/test')
def test():
    """Test API endpoint - returns a simple JSON response"""
    logger.info("Test API endpoint accessed")
    data = {
        "message": "API is working",
        "status": "OK",
        "timestamp": datetime.now().isoformat()
    }
    return jsonify(data)

@app.route('/api/echo', methods=['GET', 'POST'])
def echo():
    """Echo endpoint - returns information about the request"""
    logger.info(f"Echo endpoint accessed - method: {request.method}")
    
    data = {
        "method": request.method,
        "headers": dict(request.headers),
        "remote_addr": request.remote_addr,
        "timestamp": datetime.now().isoformat()
    }
    
    if request.method == 'POST':
        if request.is_json:
            data["json"] = request.json
        else:
            data["data"] = request.get_data(as_text=True)
    
    return jsonify(data)

@app.route('/api/debug-request')
def debug_request():
    """Debug endpoint for detailed request information"""
    logger.info("Debug request endpoint accessed")
    
    origin = request.headers.get('Origin', 'No Origin header')
    host = request.headers.get('Host', 'No Host header')
    referer = request.headers.get('Referer', 'No Referer header')
    user_agent = request.headers.get('User-Agent', 'No User-Agent header')
    x_forwarded_host = request.headers.get('X-Forwarded-Host', 'No X-Forwarded-Host header')
    x_forwarded_for = request.headers.get('X-Forwarded-For', 'No X-Forwarded-For header')
    x_forwarded_proto = request.headers.get('X-Forwarded-Proto', 'No X-Forwarded-Proto header')
    
    debug_info = {
        "method": request.method,
        "url": request.url,
        "path": request.path,
        "origin": origin,
        "host": host,
        "referer": referer,
        "user_agent": user_agent,
        "x_forwarded_host": x_forwarded_host,
        "x_forwarded_for": x_forwarded_for,
        "x_forwarded_proto": x_forwarded_proto,
        "remote_addr": request.remote_addr,
        "full_headers": dict(request.headers),
        "cookies": request.cookies,
        "args": request.args,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"Debug information: {json.dumps(debug_info, indent=2)}")
    return jsonify(debug_info)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    logger.info(f"Starting standalone minimal server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)