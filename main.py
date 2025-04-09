"""
مشاعر - خادم فلاسك بسيط لخدمة ملفات مشروع مشاعر
Mashaaer - A simple Flask server for serving Mashaaer project files
"""
import os
import logging
from flask import Flask, send_from_directory, jsonify

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint for server status"""
    return jsonify({
        "status": "healthy",
        "message": "Mashaaer server is running",
        "version": "1.0.0"
    })

@app.route('/')
def index():
    """Main index route"""
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve all other static files"""
    return send_from_directory('public', path)

# Make sure the app is available to gunicorn
# app is used by the Replit workflow that uses gunicorn
# Do not remove this file or change the app variable name

if __name__ == '__main__':
    # Start the app directly if run with python main.py
    logger.info("Starting Flask development server...")
    app.run(host='0.0.0.0', port=5000, debug=True)