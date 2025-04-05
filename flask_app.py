from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__, static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flask on Replit</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 {
                color: #2c3e50;
            }
        </style>
    </head>
    <body>
        <h1>Flask Application is Running!</h1>
        <p>This is a simple Flask application running on Replit.</p>
        <p>Server is operational and should be accessible by Replit's webview.</p>
        <p>Try accessing the <a href="/health">/health</a> endpoint to check status.</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "server": "Flask Development Server",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)