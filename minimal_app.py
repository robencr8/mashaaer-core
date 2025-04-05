"""
Ultra-Minimal Flask App for Replit Web App Feedback Tool Testing
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Minimal App Working on Port 8080</h1>"

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    print("Starting minimal app on port 8080...")
    app.run(host='0.0.0.0', port=8080)