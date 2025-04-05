"""
Absolutely minimal Flask application with no dependencies
"""
from flask import Flask

# Create a Flask app instance named 'app' for Replit compatibility
app = Flask(__name__)

@app.route('/')
def index():
    """Simplest possible root route"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mashaaer Feelings</title>
    </head>
    <body>
        <h1>Welcome to Mashaaer Feelings</h1>
        <p>The server is running correctly.</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return '{"status": "ok"}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)