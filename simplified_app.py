"""
Simplified Flask Application for Compatibility Testing
This is a minimal version of the app focused on compatibility with Replit tools.
"""
from flask import Flask, jsonify
from flask_cors import CORS
import datetime

# Create the Flask application
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Root endpoint that returns a simple JSON response"""
    return jsonify({
        "status": "online",
        "application": "Mashaaer Simplified Test App",
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/api/test')
def api_test():
    """API test endpoint"""
    return jsonify({
        "success": True,
        "message": "API endpoint working properly",
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)