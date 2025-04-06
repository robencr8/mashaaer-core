"""
Check Server Availability Script

This script attempts to connect to the local server and log the response.
It can be used to verify server connectivity from within the Replit environment.
"""
import requests
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_server_connection(url):
    """Check if server is available at the given URL"""
    try:
        logger.info(f"Attempting connection to {url}")
        response = requests.get(url, timeout=5)
        logger.info(f"Response status code: {response.status_code}")
        
        # Log headers
        logger.info("Response headers:")
        for header, value in response.headers.items():
            logger.info(f"  {header}: {value}")
        
        # Try to parse as JSON
        try:
            data = response.json()
            logger.info(f"Response data (JSON): {json.dumps(data, indent=2)}")
        except:
            # If not JSON, log the text (truncated if too long)
            text = response.text
            if len(text) > 500:
                logger.info(f"Response text (truncated): {text[:500]}...")
            else:
                logger.info(f"Response text: {text}")
        
        return True
    except requests.RequestException as e:
        logger.error(f"Connection error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    # Default URL
    url = "http://localhost:5000/api/minimal"
    
    # Use command-line argument if provided
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    success = check_server_connection(url)
    logger.info(f"Connection success: {success}")
    
    if not success:
        sys.exit(1)