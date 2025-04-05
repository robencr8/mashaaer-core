"""
Production-ready Flask application for Mashaaer Feelings
"""
from flask import Flask, jsonify, send_from_directory
import os

# Create a Flask app instance named 'app' for Replit compatibility
app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    """Main entry point for Mashaaer Feelings web application"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mashaaer Feelings</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                text-align: center;
                background-color: #f8f9fa;
            }
            h1 {
                color: #2c3e50;
                margin-top: 40px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Mashaaer Feelings</h1>
            <p>Your emotional intelligence companion</p>
            <p>The application is running correctly and ready to assist you.</p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({"status": "ok"})

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "message": "Mashaaer Feelings API is running",
        "version": "1.0.0",
        "environment": "production"
    })

@app.route('/test')
def test_page():
    """Test page for API access"""
    return send_from_directory('static', 'test_access.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)