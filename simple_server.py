"""
Simple Flask server for testing Replit web application feedback tool.
"""
from flask import Flask, jsonify, render_template_string
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Test App</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
                        Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }
        h1 {
            color: #0066cc;
            border-bottom: 2px solid #0066cc;
            padding-bottom: 10px;
        }
        .content {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .success {
            color: #00cc66;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="content">
        <h1>Simple Test App</h1>
        <p class="success">✓ Flask application is running successfully!</p>
        <p>Path: {{ request.path }}</p>
        <p>Generated at: <span id="timestamp"></span></p>
    </div>
    
    <script>
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    logger.debug("Serving index page")
    return render_template_string(HTML_TEMPLATE, request=request)

@app.route('/test')
def test():
    logger.debug("Serving test page")
    return render_template_string(HTML_TEMPLATE, request=request)

@app.route('/health')
def health():
    logger.debug("Health check requested")
    return jsonify({
        "status": "ok",
        "message": "Simple server is healthy"
    })

if __name__ == '__main__':
    from flask import request
    logger.info("Starting simple test server")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)