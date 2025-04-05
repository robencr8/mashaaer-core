"""
Ultra-Minimal Replit-Compatible Server

This is a stripped-down version focusing exclusively on compatibility
with the Replit web application feedback tool.
"""

from flask import Flask, Response

app = Flask(__name__)

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Handle OPTIONS requests
@app.route('/', methods=['OPTIONS'])
@app.route('/health', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler():
    return Response('', status=200)

@app.route('/')
def index():
    """Root route with minimal HTML"""
    html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Replit Compatible Server</title>
</head>
<body>
  <h1>Replit Compatible Server</h1>
  <p>This server is specially designed for the Replit feedback tool.</p>
</body>
</html>"""
    
    return Response(html, mimetype='text/html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return Response('{"status":"ok"}', mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)