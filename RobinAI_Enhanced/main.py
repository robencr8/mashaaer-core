"""
Compatibility Layer for Replit Deployment
This module imports and reexports the Flask app from the root main.py file
to ensure compatibility with the Replit deployment configuration.
"""

import sys
import os

# Add the parent directory to sys.path to allow importing from the root
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# Import the app from the root main.py
from main import app

# This is needed for the deployment config: gunicorn RobinAI_Enhanced.main:app
# The app object is imported from the root main.py

if __name__ == '__main__':
    # If executed directly, run the app
    app.run(host='0.0.0.0', port=5000, debug=True)