"""
Ultra-minimal Flask application for Replit testing
"""
from flask import Flask, jsonify

# Create a minimal Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Main entry point"""
    return """
    <html>
    <head>
        <title>Minimal Mashaaer Test</title>
    </head>
    <body>
        <h1>Minimal Mashaaer Test</h1>
        <p>This is a minimal test page</p>
        <a href="/health">Health Check</a>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)