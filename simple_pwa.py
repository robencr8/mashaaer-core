"""
Simplified PWA Flask application for Mashaaer Feelings

This is a minimal version that only provides the PWA functionality.
"""
from pwa_app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)