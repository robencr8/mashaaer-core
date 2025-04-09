"""
Minimal application startup for testing
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/')
def index():
    return "Mashaaer Feelings Application is running. Minimal version for testing."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)