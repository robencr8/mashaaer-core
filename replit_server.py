"""
Replit Server Configuration
This is a wrapper that configures and runs the Flask application
specifically for Replit deployment.
"""
import os
import logging
import time
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Force port to be 8080 for Replit deployment
os.environ['PORT'] = '8080'

try:
    # Import the application object from the main.py file
    from main import app
    
    logger.info("Successfully imported Flask app from main.py")
except ImportError as e:
    logger.critical(f"Failed to import Flask app: {str(e)}")
    raise

def start_server() -> None:
    """
    Start the Flask server with the correct configuration for Replit
    """
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Mashaaer Feelings on port {port}")
    
    # Display server information
    print(f"""
    =======================================================
    🚀 Mashaaer Feelings Server
    =======================================================
    🔗 URL: https://[replit-domain].repl.co/
    🔌 PORT: {port}
    📝 LOGS: Full debugging enabled
    📅 TIME: {time.strftime('%Y-%m-%d %H:%M:%S')}
    =======================================================
    """)
    
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == "__main__":
    start_server()