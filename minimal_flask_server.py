from flask import Flask, jsonify, send_from_directory, make_response, request
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()])

logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)

# Use the most permissive CORS settings for testing
CORS(app, origins='*')  # Allow all origins (INSECURE for production!)

# Create static directory if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')

# Create minimal HTML file if it doesn't exist
minimal_html_path = os.path.join('static', 'minimal.html')
if not os.path.exists(minimal_html_path):
    with open(minimal_html_path, 'w') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Minimal Test</title>
</head>
<body>
    <h1>Minimal Test Page</h1>
    <p>Server is reachable.</p>
</body>
</html>""")
    logger.info(f"Created minimal HTML file at {minimal_html_path}")

@app.route('/')
def index():
    """Root endpoint that returns a simple text response"""
    response = make_response("Minimal Flask server is running")
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Access-Control-Allow-Origin'] = '*'
    logger.info("Root endpoint accessed")
    return response

@app.route('/minimal-page')
def minimal_page():
    """Serve the minimal HTML page"""
    logger.info("Minimal page endpoint accessed")
    return send_from_directory('static', 'minimal.html')

@app.route('/api/minimal')
def minimal_api():
    """Return a simple JSON response"""
    logger.info("Minimal API endpoint accessed")
    response = jsonify({'message': 'Server is reachable'})
    # Explicitly set CORS headers for maximum compatibility
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/status', methods=['GET', 'OPTIONS'])
def api_status():
    """Simple status endpoint for the feedback tool to access"""
    logger.info(f"API status endpoint accessed with method: {request.method}")
    
    # For OPTIONS preflight requests
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    
    # For GET requests
    response = jsonify({
        'status': 'ok',
        'message': 'Minimal Flask server is running',
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    # Force the port to be 5002 to avoid conflicts
    port = 5002
    logger.info(f"Starting minimal Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)