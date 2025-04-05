"""
Ultra-simplified Test Server for Replit Feedback Tool

This is the absolute minimal Flask application designed to test
compatibility with the Replit web application feedback tool.
"""

from flask import Flask, Response

app = Flask(__name__)

@app.route('/')
def index():
    """Root route with minimal HTML"""
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Test Server</title>
</head>
<body>
  <h1>Test Server</h1>
  <p>Ultra-minimal test server is running.</p>
</body>
</html>"""
    
    response = Response(html, mimetype='text/html')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/health')
def health():
    """Health check endpoint"""
    response = Response('{"status":"ok"}', mimetype='application/json')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)