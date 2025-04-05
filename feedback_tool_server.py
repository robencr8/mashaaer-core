"""
Dedicated server for Replit web application feedback tool

This is an extremely minimal Flask application designed specifically to be compatible with
the Replit web application feedback tool, with no dependencies on other project components.
"""

from flask import Flask, Response

app = Flask(__name__)

@app.route('/')
def index():
    """Ultra-minimal root endpoint specifically for Replit web application feedback tool"""
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Mashaaer Feelings</title>
  <meta charset="UTF-8">
</head>
<body>
  <h1>Welcome to Mashaaer Feelings</h1>
  <p>This dedicated compatibility server is running correctly.</p>
</body>
</html>"""
    
    response = Response(html, mimetype='text/html')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/health')
def health():
    """Health check endpoint"""
    return Response('{"status":"ok"}', mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)