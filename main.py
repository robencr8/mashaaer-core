from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the Flask application instance
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Configure CORS with all origins allowed
CORS(app, resources={r"/*": {"origins": "*"}})

# Set a secret key for session management
app.secret_key = os.environ.get("SESSION_SECRET", "mashaaer_development_key")

@app.route('/')
def index():
    logger.debug("Serving index page")
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Mashaaer Feelings</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
                color: #333;
                background-color: #f8f8f8;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            .card {
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .status {
                display: inline-block;
                background: #2ecc71;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            a {
                color: #3498db;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Mashaaer Feelings Application</h1>
            <p>Status: <span class="status">Running</span></p>
            <p>The server is up and responding to requests.</p>
            <p>Check the <a href="/health">/health</a> endpoint for detailed status information.</p>
            <p>Server time: <script>document.write(new Date().toLocaleString());</script></p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    logger.debug("Health check requested")
    return jsonify({
        "status": "ok",
        "message": "Server is healthy",
        "version": "1.0.0",
        "timestamp": str(os.popen('date -u').read().strip())
    })

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                              'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404 error: {e}")
    return jsonify({"error": "Resource not found", "status": "error"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 error: {e}")
    return jsonify({"error": "Internal server error", "status": "error"}), 500

# This allows running the app directly with python main.py
if __name__ == "__main__":
    logger.info("Starting Mashaaer Feelings application")
    app.run(host="0.0.0.0", port=5000, debug=True)