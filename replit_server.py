"""
Replit-compatible Flask server that imports the main application.
This file is imported by Replit to serve the application.
"""
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Import the main Flask application
    from main import app
    logger.info("Successfully imported main application")
except Exception as e:
    # Fallback to a minimal app if import fails
    from flask import Flask, jsonify, redirect, url_for
    from flask_cors import CORS
    import os
    import traceback
    
    logger.error(f"Error importing main application: {str(e)}")
    logger.error(traceback.format_exc())
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/')
    def index():
        """Fallback main endpoint"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mashaaer - Service Error</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    color: #fff;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    max-width: 600px;
                    background: rgba(30, 30, 60, 0.7);
                    backdrop-filter: blur(10px);
                    border-radius: 16px;
                    padding: 30px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }
                h1 {
                    color: #9370DB;
                    margin-bottom: 20px;
                }
                p {
                    line-height: 1.6;
                }
                .button {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 20px;
                    background: linear-gradient(90deg, #9370DB, #7B68EE);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Mashaaer - Service Error</h1>
                <p>The main application couldn't be loaded properly. The system admin has been notified.</p>
                <p>Please try refreshing the page or coming back later.</p>
                <a href="/" class="button">Retry</a>
            </div>
        </body>
        </html>
        """
    
    @app.route('/direct-feedback')
    def redirect_to_main():
        """Redirect to main page in fallback mode"""
        return redirect(url_for('index'))
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            "status": "degraded",
            "error": "Main application failed to load"
        }), 500

# This code runs when testing directly with 'python replit_server.py'
if __name__ == '__main__':
    # Correct port for Replit
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
