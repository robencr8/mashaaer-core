"""
Ultra-Minimal Flask Application for Mashaaer Feelings
This file is designed to provide a bare-minimum functional API.
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Root endpoint that returns a simple HTML welcome page"""
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
            <p>Ultra Minimal Edition</p>
            <p>The application is running correctly in simplified mode.</p>
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
        "message": "Mashaaer Feelings API is running (Ultra Minimal)",
        "version": "1.0.0",
        "environment": "production"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)