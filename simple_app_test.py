"""
Simple Flask App for Testing Replit Web Application Feedback Tool

This minimal Flask application is designed to test if the Replit feedback tool
can properly connect to a simple web server running on port 8080.
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Root endpoint returning a simple message"""
    return "<h1>Hello from Simple App Test</h1><p>This is a minimal test app running on port 8080</p>"

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "app": "Simple App Test",
        "port": 8080
    })

if __name__ == '__main__':
    print("Starting simple test app on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)