

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError

app = Flask(__name__)

# Custom error handler setup
class CustomError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    response = jsonify({'error': e.description})
    response.status_code = e.code
    return response

@app.errorhandler(CustomError)
def handle_custom_error(e):
    response = jsonify({'error': e.message})
    response.status_code = e.status_code
    return response

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({'error': 'Invalid input', 'messages': e.messages}), 400
