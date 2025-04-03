"""
Ultra Minimal Flask server for testing web application accessibility

This is a standalone server that only serves a minimal HTML page
with the simplest possible configuration to help diagnose web
access issues.
"""

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins='*')  # Allow all origins for this minimal test (INSECURE for production)

@app.route('/')
def index():
    """Serve a ultra minimal HTML page"""
    logger.info("Serving ultra_minimal.html")
    return send_from_directory('static', 'ultra_minimal.html')

@app.route('/cors-test')
def cors_test():
    """Serve a page to test CORS configuration"""
    logger.info("Serving cors_test_minimal.html")
    return send_from_directory('static', 'cors_test_minimal.html')

@app.route('/api/ping')
def api_ping():
    """Simple API endpoint to test CORS configuration"""
    logger.info("API ping endpoint accessed")
    return {
        'status': 'ok',
        'message': 'Ultra minimal server is running',
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Get PORT from environment variable (Replit)
    logger.info(f"Starting ultra-minimal server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)  # Listen on all interfaces