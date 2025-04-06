#!/usr/bin/env python3
"""
Ultra Minimal Flask Server for Testing
Just serves a simple message to verify connectivity
"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "Ultra Minimal Test Server is running!"

@app.route('/healthcheck')
def healthcheck():
    return jsonify({
        "status": "ok",
        "message": "Ultra minimal test server is healthy",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    print("Starting ultra minimal test server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
