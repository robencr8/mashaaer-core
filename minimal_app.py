"""
Minimal Flask Application
This is a bare-bones Flask application to test Replit's connectivity.
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Minimal Flask App</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>Minimal Flask App</h1>
        <p>This is a minimal Flask application to test Replit's connectivity.</p>
        <p>Current time: <span id="time"></span></p>
        <p><a href="/health">Health Check</a></p>
        
        <script>
            document.getElementById('time').textContent = new Date().toLocaleString();
        </script>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "message": "Minimal Flask app is healthy"
    })

if __name__ == '__main__':
    print("Starting minimal Flask app on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)