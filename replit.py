"""
Special Replit-focused Flask application
"""
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Main page that should be detected by Replit"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hello Replit</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>Hello from Replit!</h1>
        <p>This is a minimal app for Replit's webview detection.</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/api/status')
def status():
    """API status endpoint"""
    return jsonify({
        "status": "operational",
        "server": "flask",
        "version": "1.0.0"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)