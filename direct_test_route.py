"""
Direct test route for CORS and connectivity testing

This module provides routes that serve test HTML pages for direct testing of CORS
and server connectivity.
"""
import logging
import requests
from flask import Blueprint, render_template, request, jsonify, send_from_directory

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

direct_test_bp = Blueprint('direct_test', __name__)

@direct_test_bp.route('/direct-test')
def direct_test():
    """Serve the direct test HTML page"""
    logger.debug("Serving direct test page")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Direct API Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .result { margin-top: 20px; padding: 10px; border: 1px solid #ccc; }
            .success { background-color: #dff0d8; }
            .error { background-color: #f2dede; }
            button { margin: 5px; padding: 8px 16px; }
        </style>
    </head>
    <body>
        <h1>API Direct Test</h1>
        <div>
            <button onclick="testMinimal()">Test Minimal API</button>
            <button onclick="testFeedback()">Test Feedback API</button>
            <button onclick="testCORS()">Test CORS Headers</button>
        </div>
        <div id="results" class="result"></div>

        <script>
            const resultsDiv = document.getElementById('results');
            
            function addResult(message, isSuccess) {
                const resultElem = document.createElement('div');
                resultElem.className = isSuccess ? 'success' : 'error';
                resultElem.innerHTML = message;
                resultsDiv.appendChild(resultElem);
            }
            
            async function testMinimal() {
                try {
                    const response = await fetch('/api/minimal');
                    const data = await response.json();
                    
                    addResult(`<h3>Minimal API Test: Success</h3>
                              <p>Status: ${response.status}</p>
                              <pre>${JSON.stringify(data, null, 2)}</pre>`, true);
                } catch (error) {
                    addResult(`<h3>Minimal API Test: Error</h3><p>${error.message}</p>`, false);
                }
            }
            
            async function testFeedback() {
                try {
                    const response = await fetch('/api/feedback');
                    const data = await response.json();
                    
                    addResult(`<h3>Feedback API Test: Success</h3>
                              <p>Status: ${response.status}</p>
                              <pre>${JSON.stringify(data, null, 2)}</pre>`, true);
                } catch (error) {
                    addResult(`<h3>Feedback API Test: Error</h3><p>${error.message}</p>`, false);
                }
            }
            
            async function testCORS() {
                try {
                    const response = await fetch('/api/cors-headers');
                    const data = await response.json();
                    
                    addResult(`<h3>CORS Headers Test: Success</h3>
                              <p>Status: ${response.status}</p>
                              <pre>${JSON.stringify(data, null, 2)}</pre>`, true);
                } catch (error) {
                    addResult(`<h3>CORS Headers Test: Error</h3><p>${error.message}</p>`, false);
                }
            }
        </script>
    </body>
    </html>
    """

@direct_test_bp.route('/cors-test')
def cors_test():
    """Serve the static simple test page"""
    logger.debug("Serving static simple test page")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CORS Test Page</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }
            .success { color: green; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h1>Simple CORS Test Page</h1>
        <p>This is a minimal test page for testing CORS functionality.</p>
        
        <div id="origin"></div>
        <div id="status"></div>
        <h3>CORS Test Results:</h3>
        <pre id="results"></pre>
        
        <script>
            // Display current origin
            document.getElementById('origin').innerHTML = 
                `<strong>Current Origin:</strong> ${window.location.origin}`;
            
            // Test API endpoint
            async function testAPI() {
                try {
                    document.getElementById('status').innerHTML = 
                        '<p><em>Testing API connection...</em></p>';
                    
                    // Perform a simple fetch to the API
                    const response = await fetch('/api/minimal');
                    const data = await response.json();
                    
                    // Display results
                    document.getElementById('status').innerHTML = 
                        '<p class="success">✅ Connection successful!</p>';
                    document.getElementById('results').textContent = 
                        JSON.stringify(data, null, 2);
                    
                    // Test more endpoints
                    testMoreEndpoints();
                    
                } catch (error) {
                    document.getElementById('status').innerHTML = 
                        `<p class="error">❌ Connection failed: ${error.message}</p>`;
                    console.error('API test error:', error);
                }
            }
            
            // Test additional endpoints
            async function testMoreEndpoints() {
                try {
                    // Test feedback endpoint
                    const feedbackResponse = await fetch('/api/feedback');
                    const feedbackData = await feedbackResponse.json();
                    
                    document.getElementById('results').textContent += 
                        '\\n\\n=== Feedback Endpoint ===\\n' + 
                        JSON.stringify(feedbackData, null, 2);
                    
                } catch (error) {
                    document.getElementById('results').textContent += 
                        '\\n\\n=== Feedback Endpoint Error ===\\n' + 
                        error.message;
                }
            }
            
            // Run the test immediately
            testAPI();
        </script>
    </body>
    </html>
    """

@direct_test_bp.route('/proxy-request')
def proxy_request():
    """
    Proxy a request from the server side to bypass CORS
    
    Query parameters:
        url: The URL to request
    """
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    try:
        response = requests.get(url)
        return jsonify({
            "status": response.status_code,
            "headers": dict(response.headers),
            "content": response.text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def init_direct_test(app):
    """Initialize the direct test module with the Flask app"""
    app.register_blueprint(direct_test_bp)
    logger.info("Direct test routes initialized")