"""
Mashaaer - A simple Flask server for serving Mashaaer project files
"""
import os
from flask import Flask, send_from_directory, jsonify

# Initialize Flask app
app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint for server status"""
    return jsonify({
        "status": "healthy",
        "message": "Mashaaer server is running"
    })

@app.route('/')
def index():
    """Main index route"""
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve all other static files"""
    return send_from_directory('public', path)

if __name__ == '__main__':
    # Start the app directly if run with python main.py
    app.run(host='0.0.0.0', port=5000)