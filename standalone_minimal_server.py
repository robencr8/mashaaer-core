#!/usr/bin/env python3
"""
Standalone minimal Flask server for testing the web application feedback tool

This is a completely standalone minimal server that runs on port 5000 and doesn't
require any of the dependencies of the main project. It can be used to isolate whether
the issue is with the main application or with the web application feedback tool.
"""

import logging
from datetime import datetime
from flask import Flask, make_response, request, jsonify, render_template_string

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simple HTML template for the home page
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Standalone Server</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        .info-box {
            background-color: #f0f0f0;
            border-radius: 5px;
            padding: 15px;
            margin-top: 20px;
        }
        h1 {
            color: #333;
        }
    </style>
</head>
<body>
    <h1>Standalone Minimal Server</h1>
    <p>This is a standalone Flask server designed specifically for testing the web application feedback tool.</p>
    
    <div class="info-box">
        <h2>Server Information</h2>
        <p><strong>Server Time:</strong> {{ current_time }}</p>
        <p><strong>Request Origin:</strong> {{ origin }}</p>
        <p><strong>User Agent:</strong> {{ user_agent }}</p>
    </div>
    
    <div class="info-box">
        <h2>Available Endpoints</h2>
        <ul>
            <li><a href="/">/</a> - This page</li>
            <li><a href="/api/status">/api/status</a> - API status (JSON)</li>
            <li><a href="/health">/health</a> - Health check endpoint</li>
            <li><a href="/health-check">/health-check</a> - Alternative health check</li>
            <li><a href="/test">/test</a> - Test page</li>
        </ul>
    </div>
</body>
</html>
'''

@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses"""
    origin = request.headers.get('Origin', '*')
    
    # Log the origin for debugging
    logger.info(f"Request from origin: {origin}")
    
    # Enable CORS for all origins
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Max-Age'] = '3600'  # Cache preflight for 1 hour
    
    return response

@app.route('/')
def index():
    """Root endpoint - renders a simple HTML page"""
    logger.info("Root endpoint accessed")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    origin = request.headers.get('Origin', 'No origin')
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    return render_template_string(
        HOME_TEMPLATE, 
        current_time=current_time,
        origin=origin,
        user_agent=user_agent
    )

@app.route('/api/status')
def api_status():
    """API status endpoint returning JSON data"""
    logger.info("API status endpoint accessed")
    return jsonify({
        'status': 'online',
        'server': 'standalone_minimal_server',
        'timestamp': datetime.now().isoformat(),
        'message': 'This is a standalone server for testing'
    })

@app.route('/health')
def health():
    """Simple health check endpoint"""
    logger.info("Health check endpoint accessed")
    return "OK - Server is healthy"

@app.route('/health-check')
def health_check():
    """Alternative health check endpoint"""
    logger.info("Alternative health check endpoint accessed")
    return "OK - Health check passed"

@app.route('/test')
def test():
    """Test page with minimal content"""
    logger.info("Test page accessed")
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1>Test Page</h1>
        <p>This is a simple test page from the standalone server.</p>
        <p>If you can see this, the server is working correctly!</p>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    import sys
    
    # Get port from command line argument or use default (3000)
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = 3000
            logger.warning(f"Invalid port specified: {sys.argv[1]}. Using default port 3000.")
    else:
        port = 3000
        
    logger.info(f"Starting standalone minimal server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)