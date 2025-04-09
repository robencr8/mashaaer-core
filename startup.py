"""
Fast startup script for the workflow with full application support
"""
from flask import Flask, jsonify, send_from_directory, redirect, url_for
import os

app = Flask(__name__, static_folder='public')

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/')
def index():
    """Serve the main index.html file"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from the public folder"""
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # If path doesn't exist, redirect to index
        return redirect(url_for('index'))

if __name__ == "__main__":
    # Start the Flask app directly (when not using gunicorn)
    app.run(host='0.0.0.0', port=5000, debug=True)