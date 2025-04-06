"""
Standalone Test Server
Pure minimal server designed for testing with Replit tools.
"""
from flask import Flask, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        "status": "online",
        "message": "Standalone test server is running",
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/test')
def test():
    """Test endpoint"""
    return jsonify({
        "success": True,
        "message": "Test endpoint is working"
    })

if __name__ == '__main__':
    print("Starting standalone test server on port 8888...")
    app.run(host='0.0.0.0', port=8888, debug=True)