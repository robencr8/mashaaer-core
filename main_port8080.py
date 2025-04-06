"""
Port 8080 Server Launcher for Mashaaer Feelings
This script directly imports the app from main.py and runs it on port 8080
"""
import os
import sys

# Force port to 8080
os.environ["PORT"] = "8080"

# Import the app from main
from main import app

if __name__ == "__main__":
    # Run the Flask app directly on port 8080
    print("Starting Mashaaer Feelings server on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)