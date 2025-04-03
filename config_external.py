"""
External URL Configuration for Mashaaer

This file contains configuration for external access to the application
through services like Ngrok. Update the EXTERNAL_URL when needed.
"""

import os

# Set the external URL for the application (e.g., Ngrok URL)
# This will be used in templates when generating absolute URLs
EXTERNAL_URL = os.environ.get("EXTERNAL_URL", "https://<your-ngrok-id>.ngrok-free.app")

def get_external_url():
    """
    Get the configured external URL
    
    Returns:
        str: The external URL without trailing slash
    """
    url = EXTERNAL_URL
    if url.endswith('/'):
        url = url[:-1]
    return url

def get_api_url():
    """
    Get the external API URL
    
    Returns:
        str: The external API URL
    """
    return f"{get_external_url()}/api"

def update_external_url(url):
    """
    Update the external URL (for runtime changes)
    
    Args:
        url (str): The new external URL
    """
    global EXTERNAL_URL
    EXTERNAL_URL = url
    # Also update environment variable for persistence
    os.environ["EXTERNAL_URL"] = url