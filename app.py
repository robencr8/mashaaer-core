"""
Standard Flask Application for Replit Deployment
"""
import os
import logging
from flask import Flask, jsonify, render_template, Response

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

@app.route('/')
def index():
    """Root route with minimal HTML"""
    return Response("""
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
            <p>The application is running correctly from standard app.py.</p>
        </div>
    </body>
    </html>
    """, mimetype='text/html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "message": "Mashaaer Feelings API is running",
        "version": "1.0.0",
        "environment": "production"
    })