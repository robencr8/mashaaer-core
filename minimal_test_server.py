"""
Ultra Minimal Flask Server for Testing Web Application Feedback Tool
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    """Simple root route that returns plain text"""
    return "Hello World! This is a minimal test server."

@app.route('/api/test')
def test_api():
    """Simple API endpoint that returns JSON"""
    return jsonify({"status": "ok", "message": "API is working"})

if __name__ == '__main__':
    print("Starting minimal test server on port 7000...")
    app.run(host='0.0.0.0', port=7000, debug=True)
