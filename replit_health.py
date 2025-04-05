"""
Replit Health Check

This is a very simple Flask application specifically designed to be accessible
by the Replit web application feedback tool. It provides a minimal HTTP server
with just the necessary routes for the feedback tool to function.
"""

from flask import Flask, Response, make_response

app = Flask(__name__)

@app.route('/')
def index():
    """Provide a simple HTML page that the feedback tool can access"""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Mashaaer Replit Check</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>Replit Health Check</h1>
    <p>The Mashaaer Feelings application is running correctly.</p>
    <p>This page confirms that the web server is reachable.</p>
</body>
</html>"""
    
    response = Response(html, mimetype='text/html')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

@app.route('/health')
def health():
    """Simple health check endpoint"""
    response = make_response({'status': 'ok'})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

@app.route('/', methods=['OPTIONS'])
def options():
    """Handle OPTIONS requests"""
    response = make_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)