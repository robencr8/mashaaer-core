"""
Dedicated feedback route for testing the Replit feedback tool

This module provides a dedicated route that logs all request details and returns a simple JSON response
with detailed debugging information.
"""

from flask import Blueprint, jsonify, request, current_app, render_template_string
import datetime
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

feedback_routes_bp = Blueprint('feedback_routes', __name__)

@feedback_routes_bp.route('/api/feedback', methods=['GET', 'OPTIONS'])
def feedback_route():
    """
    Dedicated feedback route for testing the Replit feedback tool
    Logs all request details and returns a simple JSON response with debug info
    """
    # Log request information
    logger.debug(f"==== FEEDBACK ROUTE DEBUG ====")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request path: {request.path}")
    logger.debug(f"Request origin: {request.headers.get('Origin', 'Not provided')}")
    
    # Log all headers
    logger.debug("Request headers:")
    for header, value in request.headers.items():
        logger.debug(f"  {header}: {value}")
    
    # Prepare response data
    data = {
        "status": "ok",
        "message": "Feedback route is working",
        "request_details": {
            "method": request.method,
            "path": request.path,
            "origin": request.headers.get('Origin', 'Not provided'),
            "headers": dict(request.headers),
            "args": dict(request.args),
        },
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Create response
    response = jsonify(data)
    
    # Add CORS headers
    origin = request.headers.get('Origin', '')
    if origin:
        # If we have an origin, echo it back to enable CORS
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        # Otherwise allow all origins
        response.headers['Access-Control-Allow-Origin'] = '*'
    
    # Add additional CORS headers
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    
    logger.debug(f"Response headers: {dict(response.headers)}")
    return response

@feedback_routes_bp.route('/feedback-test', methods=['GET'])
def feedback_test_page():
    """Serve HTML page for testing the feedback route"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Feedback Route Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #4e2a8e;
            }
            button {
                padding: 10px 15px;
                background: #4e2a8e;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin: 5px;
            }
            button:hover {
                background: #3b1f6a;
            }
            pre {
                background: #f8f8f8;
                padding: 10px;
                border-radius: 4px;
                overflow-x: auto;
                white-space: pre-wrap;
            }
            .test-result {
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Feedback Route Test</h1>
            <p>Use the buttons below to test the feedback route with different methods:</p>
            
            <div>
                <button onclick="testGet()">Test GET</button>
                <button onclick="testOptions()">Test OPTIONS (Preflight)</button>
            </div>
            
            <div class="test-result">
                <h3>Result:</h3>
                <pre id="result">Click a button to test...</pre>
            </div>
        </div>
        
        <script>
            async function testGet() {
                document.getElementById('result').textContent = 'Testing GET...';
                try {
                    const response = await fetch('/api/feedback');
                    const data = await response.json();
                    document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('result').textContent = 'Error: ' + error.message;
                }
            }
            
            async function testOptions() {
                document.getElementById('result').textContent = 'Testing OPTIONS...';
                try {
                    const response = await fetch('/api/feedback', {
                        method: 'OPTIONS',
                        headers: {
                            'Origin': window.location.origin,
                            'Access-Control-Request-Method': 'GET',
                            'Access-Control-Request-Headers': 'Content-Type'
                        }
                    });
                    
                    // Extract and display headers
                    const headers = {};
                    for (const [key, value] of response.headers.entries()) {
                        headers[key] = value;
                    }
                    
                    document.getElementById('result').textContent = 
                        'Response Status: ' + response.status + 
                        '\nResponse Headers:\n' + JSON.stringify(headers, null, 2);
                } catch (error) {
                    document.getElementById('result').textContent = 'Error: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

def register_feedback_routes(app):
    """Register feedback routes with the Flask application"""
    app.register_blueprint(feedback_routes_bp)
    logger.info("Feedback routes registered successfully")