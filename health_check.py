#!/usr/bin/env python3
"""
Extremely Minimal Health Check Server
Just responds with a simple message on port 5000
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Health check server is running!"

if __name__ == '__main__':
    print("Starting health check server on port 5000...")
    app.run(host='0.0.0.0', port=5000)