"""
Ultra-Minimal Flask App for the RobinAI_Enhanced package
This file is designed to match the expected Replit deployment entry point.
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_replit():
    return "Hello from Replit RobinAI_Enhanced!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)