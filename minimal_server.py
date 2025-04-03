"""
Minimal Flask server for testing web application accessibility

This is a standalone server that only serves a minimal HTML page
with the simplest possible configuration to help diagnose web
access issues.
"""

import os
from flask import Flask, make_response

# Initialize minimal Flask app
app = Flask(__name__)

# No CORS configuration to keep things simple

@app.route('/')
def index():
    """Serve a minimal HTML page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Minimal Test</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #121212;
                color: white;
            }
            .container {
                text-align: center;
                padding: 20px;
                border-radius: 8px;
                background-color: #2a2a2a;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            h1 {
                color: #8a2be2;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Minimal Server Test</h1>
            <p>If you can see this, the minimal test server is working!</p>
            <p>Server time: <span id="time"></span></p>
        </div>
        <script>
            document.getElementById('time').textContent = new Date().toISOString();
        </script>
    </body>
    </html>
    """
    
    # Create response with minimal HTML
    response = make_response(html)
    
    # Add explicit CORS headers to allow all origins
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Content-Type', 'text/html; charset=utf-8')
    
    return response

# Add OPTIONS handler for CORS preflight requests
@app.route('/', methods=['OPTIONS'])
def options():
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response

if __name__ == '__main__':
    # Run the app on port 5001 to avoid conflicts
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)