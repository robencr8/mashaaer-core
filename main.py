"""
Ultra Minimal Flask App for Replit Web Application Feedback Tool

This is the most minimal version possible designed specifically for compatibility.
"""

from flask import Flask, Response, jsonify, request

# Create Flask app
app = Flask(__name__, static_folder='static')

# Enable CORS for all routes with minimal configuration
@app.after_request
def add_cors_headers(response):
    # Allow requests from any origin
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response

# Handle OPTIONS requests for CORS preflight
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return Response('', status=200)

@app.route('/')
def index():
    """Root route with minimal HTML"""
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Mashaaer Feelings</title>
  <meta charset="UTF-8">
</head>
<body>
  <h1>Welcome to Mashaaer Feelings</h1>
  <p>The application is running correctly.</p>
</body>
</html>"""
    
    return Response(html, mimetype='text/html')

@app.route('/health')
def health():
    """Health check endpoint for Replit web application feedback tool"""
    return Response('{"status":"ok"}', mimetype='application/json')

@app.route('/replit-feedback-health')
def replit_feedback_health():
    """Alternative health check specifically for Replit feedback tool"""
    return Response('{"status":"ok","message":"Server is running"}', mimetype='application/json')

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return Response('{"status":"ok","message":"Server is running"}', mimetype='application/json')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return app.send_static_file(filename)

# Create app context
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
