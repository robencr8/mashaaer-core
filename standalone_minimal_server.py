"""
Standalone Minimal Server for CORS Testing

This is an ultra-minimal Flask server with maximally permissive CORS
settings for diagnosing connectivity issues with the web application feedback tool.

Usage:
  python standalone_minimal_server.py
"""

import os
import logging
import json
from datetime import datetime
from flask import Flask, request, make_response, jsonify, render_template, send_from_directory

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('standalone-server')

# Create Flask app
app = Flask(__name__)

# Global variables
PORT = int(os.environ.get('PORT', 5000))
HOST = '0.0.0.0'  # Listen on all interfaces

def add_cors_headers(response):
    """Add CORS headers to response."""
    # Get the origin from the request headers or use wildcard
    origin = request.headers.get('Origin', '*')
    
    # Log the origin for debugging
    logger.info(f"Request Origin: {origin}")
    
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = origin if origin != '*' else '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

@app.after_request
def after_request(response):
    """Add CORS headers to all responses."""
    return add_cors_headers(response)

@app.route('/', methods=['GET'])
def index():
    """Root route - return simple HTML page."""
    logger.info(f"🔍 Request: {request.method} {request.path}")
    logger.info(f"🔍 Origin: {request.headers.get('Origin', 'No Origin header')}")
    logger.info(f"🔍 Host: {request.headers.get('Host', 'No Host header')}")
    logger.info(f"🔍 User-Agent: {request.headers.get('User-Agent', 'No User-Agent header')}")
    
    logger.info("Root route accessed - detailed diagnostics:")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request remote address: {request.remote_addr}")
    
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Standalone Minimal Server</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #5c2d91; }
            .section { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .test-button { padding: 10px 15px; background-color: #5c2d91; color: white; border: none; 
                           border-radius: 5px; cursor: pointer; margin-right: 10px; }
            .test-button:hover { background-color: #4a2370; }
            #results { margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-radius: 5px; 
                      white-space: pre-wrap; }
            .success { color: green; }
            .failure { color: red; }
        </style>
    </head>
    <body>
        <h1>Standalone Minimal Server</h1>
        <div class="section">
            <h2>Server Information</h2>
            <p>This server is running on <strong>http://localhost:5000</strong> and is configured with maximally permissive CORS settings.</p>
            <p>Current time: <strong id="server-time"></strong></p>
        </div>
        
        <div class="section">
            <h2>Connection Test</h2>
            <button class="test-button" onclick="testEndpoint('/test')">Test Basic Endpoint</button>
            <button class="test-button" onclick="testEndpoint('/api/minimal')">Test Minimal API</button>
            <button class="test-button" onclick="testEndpoint('/api/ping')">Test API Ping</button>
            <div id="results">Test results will appear here...</div>
        </div>

        <script>
            // Update server time
            document.getElementById('server-time').textContent = new Date().toLocaleString();
            
            // Test endpoint function
            async function testEndpoint(endpoint) {
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = `Testing ${endpoint}...`;
                
                try {
                    const startTime = performance.now();
                    const response = await fetch(endpoint);
                    const endTime = performance.now();
                    const responseTime = (endTime - startTime).toFixed(2);
                    
                    let responseData;
                    try {
                        responseData = await response.json();
                        responseData = JSON.stringify(responseData, null, 2);
                    } catch (e) {
                        responseData = await response.text();
                    }
                    
                    const headers = {};
                    response.headers.forEach((value, key) => {
                        headers[key] = value;
                    });
                    
                    resultsDiv.innerHTML = `
                        <span class="${response.ok ? 'success' : 'failure'}">
                            ${response.ok ? '✓ Success' : '✗ Failed'}: ${response.status} ${response.statusText}
                        </span>
                        <br>Response time: ${responseTime}ms
                        <br><br><strong>Headers:</strong>
                        <pre>${JSON.stringify(headers, null, 2)}</pre>
                        <br><strong>Response:</strong>
                        <pre>${responseData}</pre>
                    `;
                } catch (error) {
                    resultsDiv.innerHTML = `
                        <span class="failure">✗ Failed: ${error.message}</span>
                    `;
                }
            }
        </script>
    </body>
    </html>
    """
    
    logger.info("Serving simple test HTML page")
    return html

@app.route('/test', methods=['GET', 'OPTIONS'])
def test():
    """Simple test endpoint returning a JSON response."""
    logger.info(f"🔍 Request: {request.method} {request.path}")
    logger.info(f"🔍 Origin: {request.headers.get('Origin', 'No Origin header')}")
    logger.info(f"🔍 Host: {request.headers.get('Host', 'No Host header')}")
    
    if request.method == 'OPTIONS':
        response = make_response()
        return add_cors_headers(response)
    
    data = {
        'message': 'Server is working!',
        'timestamp': datetime.now().isoformat(),
        'request_info': {
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'origin': request.headers.get('Origin', 'No Origin'),
        }
    }
    
    response = make_response(jsonify(data))
    logger.info(f"Sending test response: {json.dumps(data)}")
    return response

@app.route('/api/minimal', methods=['GET', 'OPTIONS'])
def api_minimal():
    """Ultra-minimal API endpoint returning a simple text response."""
    logger.info(f"🔍 Request: {request.method} {request.path}")
    logger.info(f"🔍 Origin: {request.headers.get('Origin', 'No Origin header')}")
    logger.info(f"🔍 Host: {request.headers.get('Host', 'No Host header')}")
    logger.info(f"🔍 User-Agent: {request.headers.get('User-Agent', 'No User-Agent header')}")
    
    if request.method == 'OPTIONS':
        response = make_response()
        return add_cors_headers(response)
    
    # Log detailed request information
    logger.info(f"🔍 API Request Details: {{'endpoint': '{request.path}', 'method': '{request.method}', 'args': {dict(request.args)}, 'content_type': {request.content_type}, 'has_json': {request.is_json}, 'origin': '{request.headers.get('Origin', 'No Origin header')}', 'headers': {{'Accept': '{request.headers.get('Accept', '')}', 'Accept-Encoding': '{request.headers.get('Accept-Encoding', '')}', 'Accept-Language': '{request.headers.get('Accept-Language', '')}', 'Referer': '{request.headers.get('Referer', '')}'}} }}")
    
    logger.info(f"Received {request.method} request to {request.path} from {request.headers.get('Origin', '*')}")
    
    # Create a simple text response
    response = make_response(f"Minimal API is working! Time: {datetime.now().isoformat()}")
    response.headers['Content-Type'] = 'text/plain'
    
    return response

@app.route('/api/ping', methods=['GET', 'OPTIONS'])
def api_ping():
    """Ping endpoint returning a simple JSON response."""
    logger.info(f"🔍 Request: {request.method} {request.path}")
    logger.info(f"🔍 Origin: {request.headers.get('Origin', 'No Origin header')}")
    
    if request.method == 'OPTIONS':
        response = make_response()
        return add_cors_headers(response)
    
    data = {
        'message': 'pong',
        'timestamp': datetime.now().isoformat()
    }
    
    response = make_response(jsonify(data))
    return response

if __name__ == '__main__':
    logger.info(f"Starting standalone minimal server on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True)