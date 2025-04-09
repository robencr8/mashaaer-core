"""
Direct execution script for Mashaaer
Simple startup file that listens directly on port 5000
and serves a basic health check response.
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/')
def index():
    return "Mashaaer Feelings Application is running!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)