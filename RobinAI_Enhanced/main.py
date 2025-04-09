"""
Flask Application Entry Point for RobinAI_Enhanced Package
This file imports the app from the root main.py file to maintain compatibility with Replit.
"""
import os
import sys

# Add the root directory to the path so we can import the app from main.py
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Import the app from the main file
try:
    from main import app
    print(f"Successfully imported app from {root_dir}/main.py")
except ImportError as e:
    print(f"Error importing app from main.py: {e}")
    
    # As a fallback, create a minimal app that can at least start
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mashaaer Feelings</title>
        </head>
        <body>
            <h1>Mashaaer Feelings</h1>
            <p>Warning: Running in fallback mode. The main application couldn't be loaded.</p>
        </body>
        </html>
        """
    
    @app.route('/health')
    def health():
        return jsonify({"status": "warning", "message": "Running in fallback mode"})

# This is just for local testing - when running through gunicorn, 
# the app variable above will be used directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)