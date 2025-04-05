"""
Ultra-Minimal Server Specifically for CORS Testing

This standalone server focuses solely on handling CORS configurations
with extensive logging to help diagnose issues with the Replit feedback tool.
"""

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import logging
import datetime
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cors_debug.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Apply CORS with maximally permissive settings for testing
CORS(app, 
     origins="*", 
     methods=['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE'], 
     allow_headers='*', 
     supports_credentials=False)

@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses"""
    # Get the Origin header from the request
    origin = request.headers.get('Origin')
    
    # Echo the Origin header if present, otherwise use wildcard
    response.headers['Access-Control-Allow-Origin'] = origin if origin else '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', '*')
    
    # Log the response headers (important for debugging)
    logger.debug(f"Response Headers: {dict(response.headers)}")
    
    return response

@app.route('/')
def index():
    """Simple index page for testing"""
    logger.info("Received request to index page")
    logger.debug(f"Request Headers: {dict(request.headers)}")
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ultra-Minimal CORS Test Server</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px;
                line-height: 1.6;
            }
            h1 { color: #0066cc; }
            .box {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 20px;
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Ultra-Minimal CORS Test Server</h1>
            <p>This server is specifically designed to test CORS configurations.</p>
            <p>Current time: <span id="time"></span></p>
            <ul>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/api/test-cors-minimal">Test CORS Minimal</a></li>
                <li><a href="/cors-test.html">Interactive CORS Test</a></li>
            </ul>
        </div>
        <script>
            document.getElementById('time').textContent = new Date().toLocaleString();
        </script>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Received request to health endpoint")
    logger.debug(f"Request Headers: {dict(request.headers)}")
    
    return jsonify({
        "status": "ok",
        "message": "Ultra-minimal CORS test server is healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "request_headers": dict(request.headers)
    })

@app.route('/api/test-cors-minimal', methods=['GET', 'POST', 'OPTIONS'])
def cors_test_minimal():
    """A minimal endpoint to test CORS"""
    logger.info(f"Received {request.method} request to /api/test-cors-minimal")
    logger.debug(f"Request Headers: {dict(request.headers)}")
    
    # For OPTIONS requests, we've already added CORS headers in after_request
    if request.method == 'OPTIONS':
        return jsonify({"message": "Preflight request successful"})
    
    # For GET/POST requests
    return jsonify({
        "message": "CORS test successful",
        "method": request.method,
        "timestamp": datetime.datetime.now().isoformat(),
        "request_origin": request.headers.get('Origin'),
        "request_headers": dict(request.headers)
    })

@app.route('/api/echo', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def echo_request():
    """Echo back request information for debugging"""
    logger.info(f"Received {request.method} request to /api/echo")
    logger.debug(f"Request Headers: {dict(request.headers)}")
    
    # For OPTIONS requests, we've already added CORS headers in after_request
    if request.method == 'OPTIONS':
        return jsonify({"message": "Preflight request successful"})
    
    # For other methods, echo request details
    response_data = {
        "message": "Echo request received",
        "method": request.method,
        "url": request.url,
        "headers": dict(request.headers),
        "args": dict(request.args),
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Include body data if present
    if request.json:
        response_data["json_body"] = request.json
    elif request.form:
        response_data["form_data"] = dict(request.form)
    elif request.data:
        try:
            response_data["raw_data"] = request.data.decode('utf-8')
        except:
            response_data["raw_data"] = "Binary data (could not decode as UTF-8)"
    
    return jsonify(response_data)

@app.route('/cors-test.html')
def cors_test_page():
    """Serve the interactive CORS test page"""
    logger.info("Serving interactive CORS test page")
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Interactive CORS Test</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1, h2 { color: #0066cc; }
            .box {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 20px;
                background-color: #f9f9f9;
                margin-bottom: 20px;
            }
            button {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            button:hover {
                background-color: #0052a3;
            }
            pre {
                background-color: #f1f1f1;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            .result {
                margin-top: 10px;
            }
            input[type="text"] {
                width: 100%;
                padding: 8px;
                margin-bottom: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Interactive CORS Test</h1>
            <p>This page helps you test CORS configurations with various request types.</p>

            <h2>1. Simple GET Request</h2>
            <button onclick="testGet()">Test GET Request</button>
            <div id="get-result" class="result"></div>

            <h2>2. POST Request with JSON</h2>
            <input type="text" id="post-data" value='{"text": "Test message"}' placeholder="Enter JSON data">
            <button onclick="testPost()">Test POST Request</button>
            <div id="post-result" class="result"></div>

            <h2>3. Custom Headers Test</h2>
            <input type="text" id="custom-header" value="X-Test-Header: test-value" placeholder="Enter custom header (name: value)">
            <button onclick="testCustomHeaders()">Test Custom Headers</button>
            <div id="headers-result" class="result"></div>

            <h2>4. Custom Origin Test</h2>
            <input type="text" id="custom-origin" value="https://example.com" placeholder="Enter custom origin">
            <button onclick="testCustomOrigin()">Test Custom Origin</button>
            <div id="origin-result" class="result"></div>

            <h2>5. OPTIONS Preflight Test</h2>
            <button onclick="testPreflight()">Test OPTIONS Preflight</button>
            <div id="preflight-result" class="result"></div>
        </div>

        <script>
            function displayResult(elementId, data) {
                const resultElement = document.getElementById(elementId);
                if (typeof data === 'object') {
                    resultElement.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } else {
                    resultElement.innerHTML = '<pre>' + data + '</pre>';
                }
            }

            function handleError(elementId, error) {
                console.error('Error:', error);
                displayResult(elementId, 'Error: ' + error.message);
            }

            async function testGet() {
                try {
                    const response = await fetch('/api/echo');
                    const data = await response.json();
                    displayResult('get-result', data);
                } catch (error) {
                    handleError('get-result', error);
                }
            }

            async function testPost() {
                try {
                    const jsonData = document.getElementById('post-data').value;
                    const parsedData = JSON.parse(jsonData);
                    
                    const response = await fetch('/api/echo', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(parsedData)
                    });
                    
                    const data = await response.json();
                    displayResult('post-result', data);
                } catch (error) {
                    handleError('post-result', error);
                }
            }

            async function testCustomHeaders() {
                try {
                    const headerInput = document.getElementById('custom-header').value;
                    const [headerName, headerValue] = headerInput.split(':').map(part => part.trim());
                    
                    const headers = {
                        'Content-Type': 'application/json'
                    };
                    
                    headers[headerName] = headerValue;
                    
                    const response = await fetch('/api/echo', {
                        headers: headers
                    });
                    
                    const data = await response.json();
                    displayResult('headers-result', data);
                } catch (error) {
                    handleError('headers-result', error);
                }
            }

            async function testCustomOrigin() {
                try {
                    // Note: We can't actually set the Origin header from JavaScript
                    // This is just for demonstration - it will show the actual origin
                    const origin = document.getElementById('custom-origin').value;
                    
                    displayResult('origin-result', {
                        message: "Browser security prevents setting the Origin header directly",
                        info: "The server will see the actual origin of this page",
                        requested_origin: origin,
                        actual_origin: window.location.origin
                    });
                    
                    // Make a request anyway to show what the server sees
                    const response = await fetch('/api/echo');
                    const data = await response.json();
                    
                    // Append the server's view to our result
                    const resultElement = document.getElementById('origin-result');
                    resultElement.innerHTML += '<h3>Server Response:</h3><pre>' + 
                        JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    handleError('origin-result', error);
                }
            }

            async function testPreflight() {
                try {
                    // We can't directly make an OPTIONS request with fetch
                    // But we can trigger a preflight by using a non-simple request
                    displayResult('preflight-result', {
                        message: "Making a request that will trigger a preflight OPTIONS request..."
                    });
                    
                    const response = await fetch('/api/echo', {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Custom-Header': 'trigger-preflight'
                        },
                        body: JSON.stringify({test: "preflight data"})
                    });
                    
                    const data = await response.json();
                    displayResult('preflight-result', data);
                } catch (error) {
                    handleError('preflight-result', error);
                }
            }
        </script>
    </body>
    </html>
    """

# Add special route for Replit feedback tool testing
@app.route('/replit-feedback-test')
def replit_feedback_test():
    """Endpoint specifically for the Replit feedback tool"""
    logger.info("Received request to Replit feedback test endpoint")
    logger.debug(f"Request Headers: {dict(request.headers)}")
    
    return jsonify({
        "status": "ok",
        "message": "Ultra-minimal CORS test server is responding to Replit feedback tool",
        "timestamp": datetime.datetime.now().isoformat(),
        "request_headers": dict(request.headers)
    })

if __name__ == '__main__':
    # Use port 5001 to avoid conflict with the main application
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting ultra-minimal CORS test server on port {port}...")
    app.run(debug=True, host="0.0.0.0", port=port)