"""
Ultra-Compatible Flask App for Mashaaer Feelings
Designed to work with Replit's deployment and web application feedback tool
"""

from flask import Flask, Response, jsonify, request, render_template, send_from_directory
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Add direct health check routes
@app.route('/health')
def health():
    """Main health check endpoint for Replit"""
    return Response('{"status":"ok"}', mimetype='application/json')

@app.route('/replit-health')
def replit_health():
    """Additional health check endpoint"""
    return Response('{"status":"ok"}', mimetype='application/json')

# Enable CORS for all routes
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response

# Handle OPTIONS requests for CORS preflight
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return Response('', status=200)

@app.route('/')
def index():
    """Root route with simplified HTML"""
    logger.info("Root route accessed")
    return Response("""<!DOCTYPE html>
<html>
<head>
  <title>Mashaaer Feelings</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      line-height: 1.6;
      color: #333;
      background-color: #f7f7f7;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      background-color: white;
      border-radius: 5px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    h1 {
      color: #2c3e50;
    }
    p {
      margin-bottom: 15px;
    }
    .status {
      padding: 10px;
      background-color: #e8f5e9;
      border-left: 4px solid #4caf50;
      margin-bottom: 20px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Welcome to Mashaaer Feelings</h1>
    <div class="status">
      <p>✅ The application is running correctly.</p>
    </div>
    <p>This is a bilingual (Arabic/English) responsive web application with AI-driven personalization.</p>
  </div>
</body>
</html>""", mimetype='text/html')

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    logger.info("API status endpoint accessed")
    return jsonify({
        "status": "ok",
        "message": "Server is running",
        "version": "1.0.0",
        "name": "Mashaaer Feelings API"
    })

# Create app context
if __name__ == '__main__':
    logger.info("Starting Mashaaer Feelings application")
    app.run(host='0.0.0.0', port=5000, debug=True)
