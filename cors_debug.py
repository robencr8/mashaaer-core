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
    # Serve the pre-created test page
    try:
        with open('static_test/cors_test_enhanced.html', 'r') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading test page: {e}")
        return """
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Error Loading Test Page</h1>
            <p>Could not load the test page. Please make sure static_test/cors_test_enhanced.html exists.</p>
            <p>Error: {}</p>
        </body>
        </html>
        """.format(str(e))

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