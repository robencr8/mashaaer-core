"""
Minimal Flask app for Replit testing
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    """Main entry point"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Replit Test</title>
    </head>
    <body>
        <h1>Replit Test Server</h1>
        <p>This simple server is working!</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)