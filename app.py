"""
Minimal Flask Application for Replit
"""

from flask import Flask, Response

# Create Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Root route with minimal HTML"""
    return Response("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mashaaer Feelings</title>
    </head>
    <body>
        <h1>Welcome to Mashaaer Feelings</h1>
        <p>The application is running correctly.</p>
    </body>
    </html>
    """, mimetype='text/html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return '{"status":"ok"}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)