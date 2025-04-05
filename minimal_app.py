"""
Minimal Flask application for testing Replit's feedback tool
"""
from flask import Flask
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def hello():
    logger.info("Root route accessed")
    return "Hello from Mashaaer minimal test app!"

@app.route('/health')
def health():
    logger.info("Health check accessed")
    return {"status": "ok", "service": "minimal"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)