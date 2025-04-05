"""
Extremely simple Flask application for Replit detection testing
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    """Simplest possible home route"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Replit App</title>
    </head>
    <body>
        <h1>Simple Replit Test App</h1>
        <p>This is a minimal Flask application designed to be detected by Replit.</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200

@app.route('/_health')
def _health():
    """Alternative health endpoint"""
    return "OK", 200

@app.route('/favicon.ico')
def favicon():
    """Favicon route to avoid 404 errors"""
    return "", 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)