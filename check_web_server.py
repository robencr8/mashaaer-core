"""
Check the web server status and connectivity
"""
import requests
import json
import os
import logging
import socket
import time
from pprint import pprint

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_port(port):
    """Check if a port is open on localhost"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def check_server_health(url):
    """Check if the server is healthy"""
    try:
        logger.info(f"Checking server health at {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        logger.info(f"Server health check successful: {response.status_code}")
        logger.info(f"Response: {response.text[:500]}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking server health: {e}")
        return None

def check_api_status(url):
    """Check API status"""
    try:
        logger.info(f"Checking API status at {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        logger.info(f"API status check successful: {response.status_code}")
        logger.info(f"Response: {response.text[:500]}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking API status: {e}")
        return None

def main():
    """Main function to check web server status"""
    # Check if port 5000 is open
    logger.info("Checking if port 5000 is open...")
    if check_port(5000):
        logger.info("Port 5000 is open")
    else:
        logger.error("Port 5000 is closed!")
        return

    # Base URL
    base_url = "http://localhost:5000"
    
    # Check server health
    health_data = check_server_health(f"{base_url}/health")
    if health_data:
        logger.info("Server health check passed")
        logger.info("Health data:")
        pprint(health_data)
    
    # Check API status
    api_status = check_api_status(f"{base_url}/api/status")
    if api_status:
        logger.info("API status check passed")
        logger.info("API status data:")
        pprint(api_status)
    
    # Try to get the main page
    try:
        logger.info("Trying to get the main page...")
        response = requests.get(base_url, timeout=5)
        logger.info(f"Main page status code: {response.status_code}")
        logger.info(f"Main page content type: {response.headers.get('Content-Type')}")
        logger.info(f"Main page content length: {len(response.text)} bytes")
        logger.info(f"Main page content preview: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting main page: {e}")

if __name__ == "__main__":
    main()