"""
Simplified Test Server for Replit Feedback Tool

This is an extremely minimal Flask application designed to test
compatibility with the Replit web application feedback tool.
"""

from flask import Flask, jsonify, Response, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'OPTIONS'])
def index():
    """Root route with extensive debugging information"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = Response('')
    else:
        # Regular GET request
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Replit Test Server</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>Welcome to the Test Server</h1>
    <p>This is a minimal test server for the Replit feedback tool.</p>
</body>
</html>"""
        response = Response(html, mimetype='text/html')
    
    # Add all possible CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
    
    # Debug information in console
    print(f"Received {request.method} request at {request.path}")
    print(f"Request headers: {dict(request.headers)}")
    
    return response

@app.route('/api/status', methods=['GET', 'OPTIONS'])
def status():
    """Status endpoint for health checks"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = Response('')
    else:
        # Regular GET request
        response = jsonify({
            "status": "ok",
            "message": "Server is running",
            "version": "1.0.0"
        })
    
    # Add all possible CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
    
    # Debug information in console
    print(f"Received {request.method} request at {request.path}")
    print(f"Request headers: {dict(request.headers)}")
    
    return response

@app.after_request
def after_request(response):
    """Add additional headers to all responses"""
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-Frame-Options', 'SAMEORIGIN')
    return response

if __name__ == '__main__':
    print("Starting simplified test server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)