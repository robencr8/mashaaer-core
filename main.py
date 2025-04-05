"""
Production-ready Flask application for Mashaaer Feelings
"""
from flask import Flask, jsonify, send_from_directory, render_template
import os

# Create a Flask app instance named 'app' for Replit compatibility
app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    """Main entry point for Mashaaer Feelings web application"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mashaaer Feelings</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                text-align: center;
                background-color: #f8f9fa;
            }
            h1 {
                color: #2c3e50;
                margin-top: 40px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .button {
                display: inline-block;
                padding: 10px 20px;
                margin: 10px;
                background-color: #9c27b0;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Mashaaer Feelings</h1>
            <p>Your emotional intelligence companion</p>
            <p>The application is running correctly and ready to assist you.</p>
            <div>
                <a href="/health" class="button">Health Check</a>
                <a href="/api/status" class="button">API Status</a>
                <a href="/simple-test" class="button">Test Page</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({"status": "ok"})

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "message": "Mashaaer Feelings API is running",
        "version": "1.0.0",
        "environment": "production"
    })

@app.route('/test')
def test_page():
    """Test page for API access"""
    return send_from_directory('static', 'test_access.html')

@app.route('/simple-test')
def simple_test():
    """Simple test page with direct HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mashaaer API Test</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #9c27b0;
                text-align: center;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            pre {
                background-color: #f8f8f8;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            .result {
                margin-top: 20px;
                border-left: 4px solid #9c27b0;
                padding-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Mashaaer API Test</h1>
            <p>Testing basic connectivity to the application endpoints:</p>
            
            <div class="result">
                <h3>Health Endpoint</h3>
                <pre id="health-result">Loading...</pre>
            </div>
            
            <div class="result">
                <h3>API Status Endpoint</h3>
                <pre id="api-result">Loading...</pre>
            </div>
        </div>
        
        <script>
            // Test /health endpoint
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('health-result').textContent = JSON.stringify(data, null, 2);
                })
                .catch(error => {
                    document.getElementById('health-result').textContent = 'Error: ' + error.message;
                });
                
            // Test /api/status endpoint
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('api-result').textContent = JSON.stringify(data, null, 2);
                })
                .catch(error => {
                    document.getElementById('api-result').textContent = 'Error: ' + error.message;
                });
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)