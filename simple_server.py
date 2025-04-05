"""
Ultra-Simple Flask Server for Replit Web Application Feedback Tool

This standalone server is designed to work with the Replit web application feedback tool.
It has minimal dependencies and explicitly configured CORS headers.
"""

from flask import Flask, jsonify, render_template_string
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Serve a simple HTML page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Simple Server</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
                color: #333;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .container {
                max-width: 600px;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }
            h1 {
                color: #3c3c80;
            }
            .status {
                margin-top: 20px;
                padding: 15px;
                border-radius: 4px;
                background-color: #e8f5e9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Simple Replit Test Server</h1>
            <p>This minimal server is designed to work with the Replit feedback tool.</p>
            <div class="status">
                <p>Server status: <strong>Online</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    response = app.make_response(html)
    # Add CORS headers to every response
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

@app.route('/health')
def health():
    """Health check endpoint"""
    response = jsonify({"status": "ok"})
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

@app.route('/', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path=None):
    """Handle OPTIONS requests for CORS preflight"""
    response = jsonify({})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)