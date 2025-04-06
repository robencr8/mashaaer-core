"""
Run the server directly from the command line
"""
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Force port to be 8080
os.environ['PORT'] = '8080'

if __name__ == "__main__":
    try:
        # Import the Flask app
        from main import app
        logger.info("Successfully imported Flask app")
        
        # Run on port 8080
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Starting server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)