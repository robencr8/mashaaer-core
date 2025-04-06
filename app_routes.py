"""
Main application routes for Mashaaer Feelings
"""
import os
import logging
from flask import render_template, Blueprint, jsonify, request, send_from_directory, render_template_string
import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a blueprint for app routes
app_routes_bp = Blueprint('app_routes', __name__)

@app_routes_bp.route('/app')
def app_home():
    """Serve the app homepage"""
    return render_template('index.html')

@app_routes_bp.route('/replit-access-test')
def replit_access_test():
    """Simple test page for Replit access testing"""
    test_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Replit Access Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                background-color: #f5f5f5;
                color: #333;
            }
            .test-card {
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #4a2c8f;
            }
            button {
                background: #4a2c8f;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
                margin: 5px;
                font-size: 14px;
            }
            button:hover {
                background: #6039c0;
            }
            .result {
                margin-top: 15px;
                padding: 10px;
                border-radius: 4px;
                background: #f9f9f9;
                border-left: 5px solid #4a2c8f;
            }
            .success {
                border-left-color: #5cb85c;
            }
            .error {
                border-left-color: #d9534f;
            }
            pre {
                background: #f5f5f5;
                padding: 10px;
                border-radius: 4px;
                overflow-x: auto;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="test-card">
            <h1>Replit Access Test</h1>
            <p>This page tests if the Mashaaer Feelings app is correctly accessible from the Replit domain.</p>
            <p><strong>Current Time:</strong> """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            <p><strong>Current Origin:</strong> <span id="origin"></span></p>
        </div>
        
        <div class="test-card">
            <h2>API Tests</h2>
            <button onclick="testApi('/api/minimal')">Test Minimal API</button>
            <button onclick="testApi('/api/feedback')">Test Feedback API</button>
            <button onclick="testApi('/api/health')">Test Health API</button>
            <div id="api-results"></div>
        </div>
        
        <div class="test-card">
            <h2>Debug Information</h2>
            <div id="debug-info"></div>
        </div>
        
        <script>
            // Display current origin
            document.getElementById('origin').textContent = window.location.origin;
            
            // Add debug info
            const debugInfo = {
                url: window.location.href,
                userAgent: navigator.userAgent,
                protocol: window.location.protocol,
                host: window.location.host,
                timestamp: new Date().toISOString()
            };
            document.getElementById('debug-info').innerHTML = `<pre>${JSON.stringify(debugInfo, null, 2)}</pre>`;
            
            // Function to test API endpoints
            async function testApi(endpoint) {
                const resultsDiv = document.getElementById('api-results');
                const resultElement = document.createElement('div');
                resultElement.className = 'result';
                
                try {
                    // Show loading message
                    resultElement.textContent = `Testing ${endpoint}...`;
                    resultsDiv.prepend(resultElement);
                    
                    // Make the request
                    const response = await fetch(endpoint, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        credentials: 'include'
                    });
                    
                    // Get response data
                    const data = await response.json();
                    
                    // Update with result
                    resultElement.className = 'result success';
                    resultElement.innerHTML = `
                        <h3>✅ ${endpoint} - Status: ${response.status}</h3>
                        <p><strong>CORS Headers:</strong></p>
                        <pre>Access-Control-Allow-Origin: ${response.headers.get('Access-Control-Allow-Origin') || 'Not set'}
Access-Control-Allow-Methods: ${response.headers.get('Access-Control-Allow-Methods') || 'Not set'}
Access-Control-Allow-Headers: ${response.headers.get('Access-Control-Allow-Headers') || 'Not set'}
Access-Control-Allow-Credentials: ${response.headers.get('Access-Control-Allow-Credentials') || 'Not set'}</pre>
                        <p><strong>Response Data:</strong></p>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;
                } catch (error) {
                    // Update with error
                    resultElement.className = 'result error';
                    resultElement.innerHTML = `
                        <h3>❌ ${endpoint} - Error</h3>
                        <p>${error.message}</p>
                    `;
                    console.error('API test error:', error);
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(test_html)

def register_routes(app):
    """Register all app routes with the Flask app"""
    app.register_blueprint(app_routes_bp)
    
    # We don't register the root route here as it's already defined in main.py
    
    logger.info("App routes registered successfully")