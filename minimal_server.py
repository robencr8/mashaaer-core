"""
Ultra Minimal Flask Server for Testing Feedback Tool Connectivity
Advanced diagnostic version with detailed request logging
"""
import os
import sys
import json
from flask import Flask, make_response, request, jsonify
import logging

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('minimal_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Log startup
logger.info("==== MINIMAL SERVER STARTING ====")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")

# Create a minimal Flask app without any dependencies
app = Flask(__name__)

# Log request details for diagnostics
@app.before_request
def log_request_info():
    """Log detailed information about incoming requests"""
    logger.info(f"==== REQUEST RECEIVED ====")
    logger.info(f"Path: {request.path}")
    logger.info(f"Method: {request.method}")
    logger.info(f"Origin: {request.headers.get('Origin', 'No origin')}")
    logger.info(f"User-Agent: {request.headers.get('User-Agent', 'No user agent')}")
    logger.info(f"Remote Address: {request.remote_addr}")
    logger.info(f"All Headers: {dict(request.headers)}")

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses"""
    origin = request.headers.get('Origin', '*')
    
    # If this is an OPTIONS preflight request, we need to explicitly handle it
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight request from origin: {origin}")
        response.headers['Access-Control-Allow-Origin'] = '*'  # Allow all origins for simplicity
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Max-Age'] = '3600'
        response.headers['Vary'] = 'Origin'
    else:
        # For normal requests
        response.headers['Access-Control-Allow-Origin'] = '*'  # Allow all origins for simplicity
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
    
    # Log the response details
    logger.info(f"==== RESPONSE SENT ====")
    logger.info(f"Status: {response.status_code}")
    logger.info(f"Headers: {dict(response.headers)}")
    
    return response

@app.route('/')
def index():
    """Ultra minimal root endpoint"""
    logger.info(f"Serving root endpoint")
    return "Ultra minimal server is running. This is a test page for the web application feedback tool."

@app.route('/test')
def test_api():
    """Ultra minimal test API endpoint"""
    logger.info(f"Serving test endpoint")
    
    # Return HTML for better visibility
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Endpoint</title>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>Test Endpoint</h1>
        <p style="color: green; font-weight: bold;">This endpoint is working!</p>
        <p>If you can see this message, the server is running correctly.</p>
    </body>
    </html>
    """
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    return response

@app.route('/info')
def info():
    """Show server information"""
    logger.info(f"Request to /info: {request.headers}")
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Server Info</title>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>Ultra Minimal Server Information</h1>
        <p>This is an ultra minimal server for testing feedback tool connectivity.</p>
        <ul>
            <li>Server: Flask</li>
            <li>Port: 5000</li>
            <li>CORS: Enabled (all origins)</li>
            <li>Current working directory: {os.getcwd()}</li>
        </ul>
    </body>
    </html>
    """
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    return response

@app.route('/api/status')
def api_status():
    """Simple API status endpoint"""
    logger.info(f"Serving API status endpoint")
    data = {
        "status": "ok",
        "message": "Server is running normally",
        "timestamp": str(os.path.getmtime(__file__)),
        "server_info": {
            "python_version": sys.version,
            "directory": os.getcwd()
        }
    }
    # Use jsonify for proper JSON formatting instead of string
    return jsonify(data)

@app.route('/feedback-test')
def feedback_test():
    """Special endpoint for the feedback tool testing"""
    logger.info(f"Serving feedback test endpoint")
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Feedback Tool Test</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px;">
        <h1>Feedback Tool Test Page</h1>
        <p style="color: green; font-weight: bold;">If you can see this page, the server is running correctly!</p>
        <p>This page is specifically designed for testing the web application feedback tool.</p>
        <hr>
        <p>If you're seeing this page directly in the browser, everything is working well.</p>
        <p>If you're seeing this through the feedback tool, congratulations! The connectivity issue is fixed.</p>
    </body>
    </html>
    """
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    return response

@app.route('/health-check', methods=['GET', 'OPTIONS'])
def health_check():
    """Ultra minimal health check endpoint"""
    logger.info(f"Serving health check endpoint")
    
    # If this is an OPTIONS preflight request
    if request.method == 'OPTIONS':
        return "", 200
    
    # For GET requests
    return "OK - Server is healthy", 200

if __name__ == '__main__':
    # Use a different port (8080) than the main application (5000)
    logger.info("Starting ultra minimal server on port 8080")
    app.run(host='0.0.0.0', port=8080, debug=True)