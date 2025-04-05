"""
Replit entry point for the Mashaaer Feelings application.
This file is specifically designed to work with Replit's deployment system.
"""
# Import the app from main.py
from main import app

# Replit uses this variable for deployment
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)