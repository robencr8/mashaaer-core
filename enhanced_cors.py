"""
Enhanced CORS settings for the Mashaaer Feelings application

This module provides a function to configure CORS settings that are compatible
with the Replit web application feedback tool and general cross-domain access.
"""

import os
import logging
from flask_cors import CORS

# Set up logging
logger = logging.getLogger(__name__)

def configure_enhanced_cors(app, config=None):
    """
    Configure enhanced CORS settings for maximum compatibility
    
    Args:
        app: Flask application instance
        config: Application configuration object
    """
    # Start with a base set of known origins
    origins = [
        "https://mashaaer.replit.app",
        "https://mashaaer-feelings.replit.app", 
        "https://mashaaer-ai.replit.app",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:3000",  # React development server
        "null",  # For file:// URLs
        "*"      # Allow all origins as a fallback
    ]
    
    # Add config URL if available
    if config and hasattr(config, 'APP_URL'):
        origins.append(config.APP_URL)
    
    # Add Replit-specific URLs
    if 'REPLIT_URL' in os.environ:
        origins.append(os.environ['REPLIT_URL'])
        
        # Also add the URL without https:// prefix as some tools use it
        clean_url = os.environ['REPLIT_URL'].replace('https://', '')
        origins.append(clean_url)
        
    # Add repl.co URLs if available
    if 'REPL_SLUG' in os.environ and 'REPL_OWNER' in os.environ:
        repl_co_url = f"https://{os.environ['REPL_SLUG']}.{os.environ['REPL_OWNER']}.repl.co"
        origins.append(repl_co_url)
        
        # Add without https:// prefix
        clean_repl_co_url = repl_co_url.replace('https://', '')
        origins.append(clean_repl_co_url)
    
    # Add replit.dev URLs which are used by some Replit tools
    if 'REPL_SLUG' in os.environ and 'REPL_OWNER' in os.environ:
        replit_dev_url = f"https://{os.environ['REPL_SLUG']}.{os.environ['REPL_OWNER']}.replit.dev"
        origins.append(replit_dev_url)
        
        # Add without https:// prefix
        clean_replit_dev_url = replit_dev_url.replace('https://', '')
        origins.append(clean_replit_dev_url)
    
    # Log all origins for debugging
    logger.info(f"Configuring enhanced CORS with {len(origins)} allowed origins")
    logger.debug(f"Allowed origins: {origins}")
    
    # Configure CORS with the expanded origins list and additional settings
    CORS(
        app,
        resources={r"/*": {
            "origins": origins,
            "supports_credentials": True,
            "allow_headers": [
                "Content-Type", 
                "Authorization", 
                "X-Requested-With",
                "Accept", 
                "Origin", 
                "Cache-Control"
            ],
            "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
            "expose_headers": ["Content-Length", "Content-Type"]
        }}
    )
    
    logger.info("Enhanced CORS configuration applied successfully")
    
    return origins