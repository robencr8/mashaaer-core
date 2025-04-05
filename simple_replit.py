"""
Ultra-Minimal Flask App for Replit Web App Feedback Tool Testing
with both port 5000 and 8080 routes
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Minimal App Working</h1><p>This app responds on both port 5000 and 8080</p>"

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # This port setting is only used when running directly with python
    # When using gunicorn, the port is set in the command line
    print("Starting minimal app...")
    app.run(host='0.0.0.0', port=5000)