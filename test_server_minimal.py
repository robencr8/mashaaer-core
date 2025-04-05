"""
Minimal Test Server for Replit

This is the simplest possible Flask server designed specifically
to work with the Replit web application feedback tool.
"""

from flask import Flask, Response, jsonify

# Create the Flask application
app = Flask(__name__)

@app.route('/')
def index():
    """Root endpoint returning simple HTML"""
    return Response('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Server</title>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1>Test Server</h1>
            <p>This minimal server is running.</p>
        </body>
        </html>
    ''', mimetype='text/html')

@app.route('/health')
def health():
    """Health check endpoint for Replit"""
    return jsonify({"status": "ok"})

# Enable CORS for all routes
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Start the server when script is run directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)