"""
Truly Minimal Server for testing the web application feedback tool

This is an absolute minimal Flask application with zero dependencies beyond Flask itself.
It includes a single endpoint with properly configured CORS headers.
"""

from flask import Flask, make_response

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses"""
    origin = '*'
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

@app.route('/')
def index():
    """Root endpoint - returns a simple text response"""
    return "OK - Truly Minimal Server is running"

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK"

@app.route('/test')
def test():
    """Test endpoint with JSON-like response"""
    response = make_response('{"status": "ok", "message": "Test endpoint is working"}')
    response.headers['Content-Type'] = 'application/json'
    return response

if __name__ == '__main__':
    print("Starting Truly Minimal Server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000)