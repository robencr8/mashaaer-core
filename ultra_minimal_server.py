#!/usr/bin/env python3
"""
Ultra Minimal Flask Server for Diagnostics
No dependencies other than Flask, designed for maximum reliability
"""

from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

@app.route('/')
def index():
    """Ultra minimal root endpoint"""
    return "Ultra minimal server is running"

@app.route('/test')
def test_api():
    """Ultra minimal test API endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Ultra minimal test API is working",
        "origin": request.headers.get('Origin', 'No origin')
    })

@app.route('/info')
def info():
    """Show server information"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ultra Minimal Server</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1>Ultra Minimal Server</h1>
        <p>This is an ultra minimal Flask server designed for maximum reliability.</p>
        <p>If you can see this page, the web server is accessible.</p>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    import sys
    import os
    
    # Get port from command line argument, environment variable, or default (8080)
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = int(os.environ.get('PORT', 8080))
    else:
        port = int(os.environ.get('PORT', 8080))
        
    print(f"Starting ultra minimal server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)