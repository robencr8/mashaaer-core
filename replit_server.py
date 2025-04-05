"""
Simplified Flask server for Replit compatibility testing
"""
import os
import logging
from flask import Flask, jsonify, send_file, render_template_string

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('replit_server')

# Create the Flask app
app = Flask(__name__)

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Replit Test App</title>
    <style>
        body { 
            font-family: Arial; 
            background-color: #1a1a2e;
            color: white;
            text-align: center;
            padding: 20px;
        }
        h1 { color: #8a2be2; }
        .success { color: #4caf50; }
        .error { color: #f44336; }
    </style>
</head>
<body>
    <h1>Replit Test App</h1>
    <p>This is a simple test app for Replit compatibility.</p>
    <p class="success">The server is running correctly!</p>
</body>
</html>
"""

@app.route('/')
def index():
    """Main entry point"""
    logger.info("Index page request received")
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Health check request received")
    return jsonify({
        "status": "ok",
    })

if __name__ == '__main__':
    # Use the PORT environment variable if available (for Replit compatibility)
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)