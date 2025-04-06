"""
Replit Tool Access Simulator

This script simulates a request from the Replit web application feedback tool.
It helps troubleshoot connectivity issues.
"""

import requests
import urllib.parse
import logging
import json
import sys
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def simulate_replit_tool_request(url):
    """Simulate a request from Replit feedback tool"""
    try:
        # Mock the origin of the Replit feedback tool
        headers = {
            'Origin': 'https://b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev',
            'User-Agent': 'Mozilla/5.0 (compatible; Replit-Feedback-Tool/1.0)',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev/',
        }
        
        logger.info(f"Attempting connection to {url} with Replit tool headers")
        logger.debug(f"Headers: {json.dumps(headers, indent=2)}")
        
        # Try OPTIONS request first (preflight)
        logger.info("Sending OPTIONS preflight request...")
        options_response = requests.options(
            url,
            headers={
                **headers,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=5
        )
        
        logger.info(f"OPTIONS response status code: {options_response.status_code}")
        logger.info("OPTIONS response headers:")
        for header, value in options_response.headers.items():
            logger.info(f"  {header}: {value}")
        
        # Now try the GET request
        logger.info("Sending GET request...")
        response = requests.get(url, headers=headers, timeout=5)
        
        logger.info(f"GET response status code: {response.status_code}")
        logger.info("GET response headers:")
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
        
        return options_response.status_code, response.status_code
    except requests.RequestException as e:
        logger.error(f"Connection error: {str(e)}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None, None

if __name__ == "__main__":
    # Default URL
    url = "http://localhost:5000/api/minimal"
    
    # Use command-line argument if provided
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    # Set the environment variable for feedback tool origin
    os.environ['FEEDBACK_TOOL_ORIGIN'] = 'https://b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev'
    
    options_status, get_status = simulate_replit_tool_request(url)
    
    logger.info(f"Simulation result: OPTIONS: {options_status}, GET: {get_status}")
    
    if options_status in (200, 204) and get_status == 200:
        logger.info("✅ SUCCESS: The server properly responded to both requests")
        sys.exit(0)
    else:
        logger.error("❌ FAILURE: The server did not respond correctly to the requests")
        sys.exit(1)