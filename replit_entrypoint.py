"""
Replit Entry Point - Ultra Minimal Version
This file is designed to match the workflow configuration.
"""
# Import the Flask app instance from the main.py file
from main import app

# That's it! No need for anything else.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)