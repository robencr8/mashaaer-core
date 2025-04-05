"""
Ultra-simple test application for the Replit web application feedback tool
"""

from flask import Flask, render_template, request, jsonify, Response

app = Flask(__name__)

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
  <p><a href="/cosmic-onboarding">Start Cosmic Onboarding</a></p>
</body>
</html>"""
    
    response = Response(html, mimetype='text/html')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/status')
def api_status():
    """Simple API status endpoint"""
    return jsonify({
        'status': 'online',
        'message': 'API is running correctly'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)