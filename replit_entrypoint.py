"""
Simple entrypoint for Replit deployment
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    """Main entry point"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Replit Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
            }
            h1 {
                color: #444;
            }
            .success {
                color: green;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h1>Replit Test Server</h1>
        <p class="success">✓ The server is working correctly!</p>
        <p>This is a simplified test app to verify Replit connectivity.</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)