"""
Ultra Minimal Flask Server for Testing Feedback Tool Connectivity
"""
import os
from flask import Flask, make_response, request
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='minimal_server.log'
)
logger = logging.getLogger(__name__)

# Create a minimal Flask app without any dependencies
app = Flask(__name__)

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

@app.route('/')
def index():
    """Ultra minimal root endpoint"""
    logger.info(f"Request to /: {request.headers}")
    return "Ultra minimal server is running"

@app.route('/test')
def test_api():
    """Ultra minimal test API endpoint"""
    logger.info(f"Request to /test: {request.headers}")
    return "Test endpoint is working"

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
    logger.info(f"Request to /api/status: {request.headers}")
    data = {
        "status": "ok",
        "message": "Server is running normally"
    }
    resp = make_response(str(data))
    resp.headers['Content-Type'] = 'application/json'
    return resp

if __name__ == '__main__':
    logger.info("Starting ultra minimal server on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)