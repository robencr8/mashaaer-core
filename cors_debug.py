"""
CORS Debug Server

A minimal Flask server specifically designed for CORS debugging with extensive logging.
This server isolates CORS functionality to help diagnose issues with the Replit feedback tool.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import traceback
import datetime
import json

# Configure logging (highly recommended)
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
# CORS: Allow all origins, methods, and headers for this *minimal* test (INSECURE for production)
CORS(app, origins="*", methods=['GET', 'POST', 'OPTIONS'], allow_headers='*', supports_credentials=True)

@app.after_request
def add_cors_headers(response):
    """Explicitly add CORS headers to all responses for maximum compatibility"""
    # Get the Origin header from the request
    origin = request.headers.get('Origin')
    
    # Echo the Origin header if present, otherwise use wildcard
    response.headers['Access-Control-Allow-Origin'] = origin if origin else '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    # Log the response headers (important for debugging)
    logger.debug(f"Response Headers: {dict(response.headers)}")
    
    return response

@app.route('/')
def index():
    """Main page with links to test endpoints"""
    logger.info("Accessed index page")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CORS Debug Server</title>
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
            ul { 
                padding-left: 20px; 
            }
            li {
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>CORS Debug Server</h1>
            <p>This is a minimal server for testing CORS configurations.</p>
            <h2>Test Endpoints:</h2>
            <ul>
                <li><a href="/api/test-cors-minimal">Simple GET Test</a></li>
                <li><a href="/test-cors">Interactive CORS Test Page</a></li>
                <li><a href="/health">Health Check</a></li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Health check requested")
    logger.debug(f"Request Headers: {dict(request.headers)}")
    
    return jsonify({
        "status": "ok",
        "message": "CORS debug server is healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "request_headers": dict(request.headers)
    })

@app.route('/api/test-cors-minimal', methods=['GET', 'POST', 'OPTIONS'])
def cors_test_minimal():
    """A minimal endpoint to test CORS"""
    logger.info(f"Received request to /api/test-cors-minimal: {request.method} {request.url}")

    try:
        # Log request details
        logger.debug(f"Request Headers: {dict(request.headers)}")
        if request.method == 'POST' and request.is_json:
            try:
                logger.debug(f"Request Body: {request.get_json()}")
            except Exception as e:
                logger.debug(f"Could not parse request body as JSON: {e}")

        # Echo the Origin header if present, otherwise, allow all
        origin = request.headers.get('Origin')
        
        # Construct a minimal response with the echoed Origin
        response_data = {
            'message': 'CORS test successful', 
            'request_origin': origin, 
            'request_headers': dict(request.headers),
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        logger.error(traceback.format_exc())  # Log the full traceback
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@app.route('/test-cors')
def test_cors_ui():
    """Serve the enhanced CORS test page"""
    logger.info("Accessed CORS test page")
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enhanced CORS Test Page</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
            }
            h1, h2 { color: #0066cc; }
            button { 
                padding: 10px 20px; 
                cursor: pointer; 
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            button:hover {
                background-color: #004c99;
            }
            .result-container {
                margin-top: 20px;
                border: 1px solid #ddd;
                padding: 15px;
                border-radius: 4px;
                background-color: #f9f9f9;
            }
            .result {
                background-color: #f1f1f1;
                padding: 10px;
                border-radius: 4px;
                font-family: monospace;
                white-space: pre-wrap;
                overflow-x: auto;
                max-height: 300px;
                overflow-y: auto;
            }
            .section {
                margin-bottom: 20px;
                padding-bottom: 20px;
                border-bottom: 1px solid #eee;
            }
            input[type="text"], textarea {
                width: 100%;
                padding: 8px;
                margin-bottom: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            .status-success {
                color: green;
                font-weight: bold;
            }
            .status-error {
                color: red;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h1>Enhanced CORS Test Page</h1>
        <p>This page sends requests to test CORS configuration.</p>
        
        <div class="section">
            <h2>1. Simple GET Request</h2>
            <button onclick="testGetRequest()">Test GET Request</button>
            <div class="result-container">
                <h3>Result:</h3>
                <div id="get-result" class="result">Results will appear here...</div>
            </div>
        </div>
        
        <div class="section">
            <h2>2. POST Request with JSON</h2>
            <textarea id="post-data" rows="4" placeholder="Enter JSON data">{"text": "Testing CORS with POST request", "detail": true}</textarea>
            <button onclick="testPostRequest()">Test POST Request</button>
            <div class="result-container">
                <h3>Result:</h3>
                <div id="post-result" class="result">Results will appear here...</div>
            </div>
        </div>
        
        <div class="section">
            <h2>3. Request with Custom Headers</h2>
            <input type="text" id="custom-header-name" placeholder="Header Name (e.g., X-Custom-Header)" value="X-Custom-Header">
            <input type="text" id="custom-header-value" placeholder="Header Value" value="test-value">
            <button onclick="testCustomHeaders()">Test Custom Headers</button>
            <div class="result-container">
                <h3>Result:</h3>
                <div id="header-result" class="result">Results will appear here...</div>
            </div>
        </div>
        
        <div class="section">
            <h2>4. CORS Preflight Test</h2>
            <p>This will trigger a preflight OPTIONS request by using custom headers.</p>
            <button onclick="testPreflightRequest()">Test Preflight Request</button>
            <div class="result-container">
                <h3>Result:</h3>
                <div id="preflight-result" class="result">Results will appear here...</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Browser Information</h2>
            <div class="result-container">
                <div id="browser-info" class="result">Loading browser info...</div>
            </div>
        </div>

        <script>
            // Display browser information on load
            window.onload = function() {
                const browserInfo = document.getElementById('browser-info');
                browserInfo.textContent = `User Agent: ${navigator.userAgent}\n`;
                browserInfo.textContent += `Current Origin: ${window.location.origin}\n`;
                browserInfo.textContent += `Current URL: ${window.location.href}\n`;
                browserInfo.textContent += `Time: ${new Date().toLocaleString()}\n`;
            };
            
            // Helper function to display results
            function displayResult(elementId, status, message) {
                const resultElement = document.getElementById(elementId);
                const timestamp = new Date().toLocaleTimeString();
                
                if (status === 'success') {
                    resultElement.innerHTML = `<span class="status-success">[${timestamp}] Success:</span>\n${message}`;
                } else {
                    resultElement.innerHTML = `<span class="status-error">[${timestamp}] Error:</span>\n${message}`;
                }
            }
            
            // Test simple GET request
            async function testGetRequest() {
                const resultElement = document.getElementById('get-result');
                resultElement.textContent = 'Sending GET request...';
                
                try {
                    const response = await fetch('/api/test-cors-minimal');
                    
                    // Format headers for display
                    let headersText = 'Response Headers:\\n';
                    response.headers.forEach((value, name) => {
                        headersText += `${name}: ${value}\\n`;
                    });
                    
                    const data = await response.json();
                    const formattedData = JSON.stringify(data, null, 2);
                    
                    displayResult('get-result', 'success', 
                        `Status: ${response.status} ${response.statusText}\\n\\n${headersText}\\n` +
                        `Response Data:\\n${formattedData}`);
                } catch (error) {
                    displayResult('get-result', 'error', 
                        `Error making GET request:\\n${error.message}\\n\\n` +
                        `Check browser console for more details.`);
                    console.error('GET Request Error:', error);
                }
            }
            
            // Test POST request with JSON body
            async function testPostRequest() {
                const resultElement = document.getElementById('post-result');
                resultElement.textContent = 'Sending POST request...';
                
                try {
                    // Get and parse the JSON data from the textarea
                    const jsonDataText = document.getElementById('post-data').value;
                    let jsonData;
                    
                    try {
                        jsonData = JSON.parse(jsonDataText);
                    } catch (parseError) {
                        displayResult('post-result', 'error', 
                            `Invalid JSON data:\\n${parseError.message}`);
                        return;
                    }
                    
                    const response = await fetch('/api/test-cors-minimal', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(jsonData)
                    });
                    
                    // Format headers for display
                    let headersText = 'Response Headers:\\n';
                    response.headers.forEach((value, name) => {
                        headersText += `${name}: ${value}\\n`;
                    });
                    
                    const data = await response.json();
                    const formattedData = JSON.stringify(data, null, 2);
                    
                    displayResult('post-result', 'success', 
                        `Status: ${response.status} ${response.statusText}\\n\\n${headersText}\\n` +
                        `Response Data:\\n${formattedData}`);
                } catch (error) {
                    displayResult('post-result', 'error', 
                        `Error making POST request:\\n${error.message}\\n\\n` +
                        `Check browser console for more details.`);
                    console.error('POST Request Error:', error);
                }
            }
            
            // Test request with custom headers
            async function testCustomHeaders() {
                const resultElement = document.getElementById('header-result');
                resultElement.textContent = 'Sending request with custom headers...';
                
                try {
                    const headerName = document.getElementById('custom-header-name').value;
                    const headerValue = document.getElementById('custom-header-value').value;
                    
                    if (!headerName || !headerValue) {
                        displayResult('header-result', 'error', 
                            'Please enter both header name and value');
                        return;
                    }
                    
                    const headers = {
                        'Content-Type': 'application/json'
                    };
                    headers[headerName] = headerValue;
                    
                    const response = await fetch('/api/test-cors-minimal', {
                        headers: headers
                    });
                    
                    // Format headers for display
                    let headersText = 'Response Headers:\\n';
                    response.headers.forEach((value, name) => {
                        headersText += `${name}: ${value}\\n`;
                    });
                    
                    let requestHeadersText = 'Request Headers Sent:\\n';
                    for (const [name, value] of Object.entries(headers)) {
                        requestHeadersText += `${name}: ${value}\\n`;
                    }
                    
                    const data = await response.json();
                    const formattedData = JSON.stringify(data, null, 2);
                    
                    displayResult('header-result', 'success', 
                        `${requestHeadersText}\\n` +
                        `Status: ${response.status} ${response.statusText}\\n\\n${headersText}\\n` +
                        `Response Data:\\n${formattedData}`);
                } catch (error) {
                    displayResult('header-result', 'error', 
                        `Error making request with custom headers:\\n${error.message}\\n\\n` +
                        `Check browser console for more details.`);
                    console.error('Custom Headers Request Error:', error);
                }
            }
            
            // Test preflight request
            async function testPreflightRequest() {
                const resultElement = document.getElementById('preflight-result');
                resultElement.textContent = 'Sending request that triggers preflight...';
                
                try {
                    // This request should trigger a preflight because of:
                    // 1. Non-simple method (PUT)
                    // 2. Custom headers
                    const response = await fetch('/api/test-cors-minimal', {
                        method: 'PUT',  // Non-simple method
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Preflight-Test': 'true',  // Custom header
                            'X-Custom-Auth': 'preflight-test'  // Another custom header
                        },
                        body: JSON.stringify({
                            text: 'This request should trigger a preflight',
                            test: true
                        })
                    });
                    
                    // Format headers for display
                    let headersText = 'Response Headers:\\n';
                    response.headers.forEach((value, name) => {
                        headersText += `${name}: ${value}\\n`;
                    });
                    
                    try {
                        const data = await response.json();
                        const formattedData = JSON.stringify(data, null, 2);
                        
                        displayResult('preflight-result', 'success', 
                            `Preflight should have been sent before this request.\\n` +
                            `Status: ${response.status} ${response.statusText}\\n\\n${headersText}\\n` +
                            `Response Data:\\n${formattedData}\\n\\n` +
                            `Note: Check browser Network tab to see the OPTIONS preflight request.`);
                    } catch (e) {
                        // Handle non-JSON response
                        const text = await response.text();
                        displayResult('preflight-result', 'success', 
                            `Preflight should have been sent before this request.\\n` +
                            `Status: ${response.status} ${response.statusText}\\n\\n${headersText}\\n` +
                            `Response Text:\\n${text}\\n\\n` +
                            `Note: Check browser Network tab to see the OPTIONS preflight request.`);
                    }
                } catch (error) {
                    displayResult('preflight-result', 'error', 
                        `Error with preflight request:\\n${error.message}\\n\\n` +
                        `This likely means the preflight OPTIONS request failed.\\n` +
                        `Check browser console and Network tab for more details.`);
                    console.error('Preflight Request Error:', error);
                }
            }
        </script>
    </body>
    </html>
    """

@app.route('/replit-feedback-test')
def replit_feedback_test():
    """Special endpoint specifically for the Replit feedback tool"""
    logger.info("Replit feedback test requested")
    logger.debug(f"Request Headers: {dict(request.headers)}")
    
    return jsonify({
        "status": "ok",
        "message": "CORS debug server responding to Replit feedback tool",
        "timestamp": datetime.datetime.now().isoformat(),
        "origin": request.headers.get('Origin', 'Unknown'),
        "request_headers": dict(request.headers)
    })

if __name__ == '__main__':
    # Use port 5010 to avoid conflict with other servers
    port = int(os.environ.get('PORT', 5010))
    try:
        logger.info(f"Starting CORS debug server on port {port}...")
        app.run(debug=True, host="0.0.0.0", port=port)
    except Exception as e:
        logger.critical(f"Error starting Flask app: {e}")
        logger.critical(traceback.format_exc())