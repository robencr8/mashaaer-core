"""
Ultra-Simple Test Server

This is the absolute minimal Flask application designed for Replit web application feedback tool.
"""

from flask import Flask, Response, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'OPTIONS'])
def index():
    """Root route with minimal HTML"""
    # For OPTIONS requests
    if request.method == 'OPTIONS':
        response = Response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # For GET requests
    html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Ultra Simple Server</title>
</head>
<body>
  <h1>Ultra Simple Server</h1>
  <p>This server is running and accessible to the Replit feedback tool.</p>
</body>
</html>"""
    
    response = Response(html, mimetype='text/html')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    """Health check endpoint specifically for the Replit feedback tool"""
    # For OPTIONS requests
    if request.method == 'OPTIONS':
        response = Response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    # For GET requests
    response = Response('{"status":"ok"}', mimetype='application/json')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Only run the server if this script is executed directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)