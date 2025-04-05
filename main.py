"""
Ultra-Minimal Flask Application for Replit Feedback Tool
This file is deliberately ultra-simple to ensure compatibility
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)