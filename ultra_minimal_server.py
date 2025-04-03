"""
Ultra Minimal Server for testing the web application feedback tool

This is a self-contained Flask application with minimal dependencies that can be used
to test if the web application feedback tool can successfully connect to a server.
It includes properly configured CORS headers and a simple health check endpoint.
"""

import os
import logging
from datetime import datetime

from flask import Flask, jsonify, make_response, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# CORS headers helper function
def add_cors_headers(response):
    """Add CORS headers to the response"""
    origin = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

@app.route('/')
def index():
    """Root endpoint - returns a simple HTML page"""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Ultra Minimal Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .success { color: green; }
    </style>
</head>
<body>
    <h1>Ultra Minimal Server</h1>
    <p class="success">✅ Server is running!</p>
    <p>Server time: {time}</p>
    <p><a href="/api/test">Test API Endpoint</a></p>
</body>
</html>""".format(time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    return add_cors_headers(response)

@app.route('/api/test')
def test_api():
    """Test API endpoint - returns a simple JSON response"""
    data = {
        "status": "success",
        "message": "API is working",
        "timestamp": datetime.now().isoformat()
    }
    response = jsonify(data)
    return add_cors_headers(response)

@app.route('/health')
def health():
    """Simple health check endpoint - returns text 'OK'"""
    response = make_response("OK")
    response.headers['Content-Type'] = 'text/plain'
    return add_cors_headers(response)

@app.route('/echo', methods=['GET', 'POST', 'OPTIONS'])
def echo():
    """Echo endpoint - returns information about the request"""
    if request.method == 'OPTIONS':
        response = make_response()
        return add_cors_headers(response)
    
    data = {
        "method": request.method,
        "headers": dict(request.headers),
        "args": dict(request.args),
        "form": dict(request.form) if request.form else None,
        "json": request.json if request.is_json else None,
        "timestamp": datetime.now().isoformat()
    }
    
    # Clean up sensitive data before logging
    log_data = data.copy()
    if 'headers' in log_data and log_data['headers']:
        for sensitive in ['Authorization', 'Cookie']:
            if sensitive in log_data['headers']:
                log_data['headers'][sensitive] = '[REDACTED]'
    
    logger.info(f"Echo request: {log_data}")
    response = jsonify(data)
    return add_cors_headers(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Use port 8080 instead
    logger.info(f"Starting ultra minimal server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)