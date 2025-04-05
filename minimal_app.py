"""
Minimal Flask Application for Replit Deployment
"""

from flask import Flask, render_template_string
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create app
app = Flask(__name__)

@app.route('/')
def index():
    """Root route with minimal HTML"""
    logger.info("Minimal app index page requested")
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mashaaer Minimal</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                color: white;
            }
            .container {
                text-align: center;
                padding: 2rem;
                border-radius: 1rem;
                background-color: rgba(0,0,0,0.3);
            }
            h1 { color: #a170ff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Mashaaer Minimal</h1>
            <p>PWA-enabled application is running</p>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Health check endpoint requested")
    return {"status": "healthy", "message": "Minimal app is running"}

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    logger.info("API status endpoint requested")
    return {"status": "online", "message": "Minimal API is running", "version": "1.0.0"}

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)