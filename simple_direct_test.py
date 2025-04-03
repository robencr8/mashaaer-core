from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os

app = Flask(__name__, template_folder='templates')
CORS(app, origins="*", supports_credentials=True)

@app.route('/')
def index():
    # First try to serve the diagnostic.html template
    if os.path.exists(os.path.join('templates', 'diagnostic.html')):
        return render_template('diagnostic.html')
    
    # Fallback to JSON response
    return jsonify({
        "status": "online",
        "message": "Simple test server is running on port 8080",
    })

@app.route('/test')
def test():
    return jsonify({
        "status": "success",
        "message": "Test endpoint reached successfully"
    })

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "online",
        "service": "Simple Test API",
        "version": "1.0",
        "serverTime": "2025-04-03T04:54:00Z",
        "environment": "development"
    })

if __name__ == "__main__":
    print("Starting simple test server on port 8080...")
    app.run(host="0.0.0.0", port=8080, debug=True)