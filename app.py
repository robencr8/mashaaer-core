from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

class APIError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.payload if error.payload else {'error': error.message})
    response.status_code = error.status_code
    logger.error(f"API Error: {error.message} (Status: {error.status_code})")
    return response

@app.errorhandler(HTTPException)
def handle_http_exception(error):
    response = jsonify({'error': error.description})
    response.status_code = error.code
    logger.error(f"HTTP Exception: {error.description} (Status: {error.code})")
    return response

@app.errorhandler(Exception)
def handle_unexpected_exception(error):
    logger.exception("Unexpected exception occurred")
    response = jsonify({'error': 'An unexpected error occurred'})
    response.status_code = 500
    return response