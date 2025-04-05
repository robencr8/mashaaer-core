"""
Ultra Minimal Flask App for Replit Web Application Feedback Tool
"""

from flask import Flask, Response

# Create Flask app
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
</body>
</html>"""
    
    return Response(html, mimetype='text/html')

@app.route('/health')
def health():
    """Health check endpoint for Replit web application feedback tool"""
    return Response('{"status":"ok"}', mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)