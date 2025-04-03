#!/usr/bin/env python3
"""
Truly Minimal Server - No CSS, no fancy formatting, just plain HTML and JSON
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Simplest possible home page"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Minimal Server</title></head>
    <body>
        <h1>Minimal Server</h1>
        <p>Server is running!</p>
        <p><a href="/api/test">Test API Endpoint</a></p>
    </body>
    </html>
    """

@app.route('/api/test')
def test_api():
    """Simple API test endpoint"""
    return jsonify({"status": "success", "message": "API is working"})

@app.route('/health')
def health():
    """Ultra minimal health check endpoint"""
    return "OK"

@app.route('/echo')
def echo():
    """Echo request info"""
    return "Echo endpoint is working"

@app.after_request
def add_cors_headers(response):
    """Add CORS headers to every response"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting minimal server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)