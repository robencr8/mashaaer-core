"""
Basic Flask App with proper configuration for Mashaaer
"""
import os
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "mashaaer-secret-key-2025")

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Mashaaer app is running",
        "version": "1.0.0"
    })

@app.route('/')
def index():
    """Main index route"""
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve all other static files"""
    return send_from_directory('public', path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)