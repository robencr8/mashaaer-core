"""
Compatibility Layer for Replit Deployment
This module imports and reexports the Flask app from the root main.py file
to ensure compatibility with the Replit deployment configuration.
"""
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the app from the root main.py
from main import app

# This file exists solely to provide the correct import path for the .replit file