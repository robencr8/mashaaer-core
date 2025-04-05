"""
Enhanced Minimal Flask App for Replit
Uses the Flask variable name 'app' expected by Replit
Adds improved logging and CORS support to troubleshoot connection issues
"""
from flask import Flask, render_template_string, send_from_directory, request, jsonify
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a Flask app instance named 'app' for Replit compatibility
app = Flask(__name__)

# Enable CORS for all routes - this is important for the Replit feedback tool
CORS(app, supports_credentials=True, origins="*")

@app.route('/')
def index():
    """
    Return a simple HTML page for maximum compatibility with Replit
    """
    logger.debug(f"Received request for index from: {request.remote_addr}")
    logger.debug(f"Request headers: {request.headers}")
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mashaaer Feelings</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <h1>Welcome to Mashaaer Feelings</h1>
        <p>The server is running correctly.</p>
        <p>Time of page load: <span id="time"></span></p>
        <script>
            document.getElementById('time').textContent = new Date().toISOString();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.debug(f"Received health check from: {request.remote_addr}")
    logger.debug(f"Request headers: {request.headers}")
    return jsonify({"status": "ok"})

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    logger.debug(f"Received API status request from: {request.remote_addr}")
    logger.debug(f"Request headers: {request.headers}")
    return jsonify({
        "message": "Server is running",
        "version": "1.0.0",
        "environment": "replit"
    })

@app.route('/<path:path>')
def serve_file(path):
    """Serve static files"""
    logger.debug(f"Received request for file: {path} from: {request.remote_addr}")
    if os.path.exists(path):
        return send_from_directory('.', path)
    else:
        return index()