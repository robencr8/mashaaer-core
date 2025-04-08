from flask import Flask, send_from_directory, render_template, redirect
import os
from flask_cors import CORS

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('public', path)):
        return send_from_directory('public', path)
    else:
        return send_from_directory('public', 'index.html')

if __name__ == '__main__':
    # Use port 8000 instead of 5000 for compatibility with Replit's env
    app.run(host='0.0.0.0', port=8000, debug=True)