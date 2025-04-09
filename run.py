"""
Fast and direct server for Mashaaer app with cosmic effects
"""
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='public')

@app.route('/')
def index():
    """Serve the main index.html file"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from the public folder"""
    return send_from_directory(app.static_folder, path)

@app.route('/health')
def health_check():
    """Health check endpoint for workflow"""
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting Mashaaer server on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)