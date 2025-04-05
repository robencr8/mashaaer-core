"""
Simple Flask application for Replit testing

This is a simplified version of the main.py file for testing Replit's web server capabilities.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import os
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main')

# Create and configure the Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    """Main entry point for testing Replit web server connection"""
    logger.info(f"Index page request received from {request.remote_addr}")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Replit Test</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
                background-color: #f5f5f5;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            .success {{
                color: #27ae60;
                font-weight: bold;
                background-color: #e8f5e9;
                padding: 10px;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .info {{
                background-color: #e3f2fd;
                padding: 15px;
                border-radius: 4px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <h1>Replit Test Server</h1>
        <div class="success">✓ The server is working correctly!</div>
        <p>This is a simplified test page to verify Replit's web server connectivity.</p>
        <div class="info">
            <p><strong>Server timestamp:</strong> {timestamp}</p>
            <p><strong>Request IP:</strong> {request.remote_addr}</p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    # Add CORS headers explicitly
    response = jsonify({
        "status": "ok",
        "time": datetime.datetime.now().isoformat(),
        "environment": "replit",
        "app_version": "1.0.0",
        "request_info": {
            "url": request.url,
            "method": request.method,
            "remote_addr": request.remote_addr,
            "host": request.host,
            "user_agent": request.user_agent.string
        }
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response

@app.route('/hello')
def hello():
    """Simplest possible route to check server is responding"""
    return "Hello from Replit Flask Server!"

@app.route('/replit-health')
def replit_health():
    """Special health endpoint for Replit verification"""
    return "OK"

@app.route('/replit-test')
def replit_test():
    """Test page specifically for Replit's feedback tool"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Replit Test Page</title>
    </head>
    <body>
        <h1>Replit Test Page</h1>
        <p>This page is specifically designed for Replit's feedback tool verification.</p>
    </body>
    </html>
    """

@app.route('/_health')
def _health():
    """Alternative health check endpoint for Replit verification"""
    return "OK"

@app.route('/_status')
def _status():
    """Status endpoint for Replit verification"""
    return "OK"

@app.route('/replit-verify')
def replit_verify():
    """Dedicated endpoint for Replit verification tools"""
    return "OK - Replit verification"

@app.route('/favicon.ico')
def favicon():
    """Favicon handler to avoid 404 errors"""
    return "", 204

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)