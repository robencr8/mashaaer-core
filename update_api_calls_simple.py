#!/usr/bin/env python3
"""
A simpler approach to update the fetch calls in cosmic_onboarding.html
using string methods instead of complex regex patterns.
"""
import os
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def update_fetch_calls(filepath):
    """
    Updates fetch() calls in the given HTML file to use POST for /api/listen-for-voice.
    Uses simple string replacement rather than complex regex.
    
    Args:
        filepath: The path to the HTML file.
    
    Returns:
        bool: True if updates were successful, False otherwise
    """
    try:
        # Read the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # The target pattern to look for
        old_pattern = "fetch('/api/listen-for-voice?language=' + userLanguage)"
        
        # The replacement with POST method
        new_pattern = """fetch('/api/listen-for-voice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          language: userLanguage
        })
      })"""
        
        # Check if the pattern exists in the content
        if old_pattern not in content:
            logger.warning(f"Pattern not found in {filepath}")
            return False
        
        # Replace all occurrences of the old pattern with the new one
        updated_content = content.replace(old_pattern, new_pattern)
        
        # Check if any replacements were made
        if content == updated_content:
            logger.warning(f"No replacements made in {filepath}")
            return False
        
        # Write the updated content back to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
            
        logger.info(f"Successfully updated fetch() calls in {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating {filepath}: {e}")
        return False

if __name__ == "__main__":
    # Try both potential paths for the file
    potential_paths = [
        "./cosmic_onboarding.html",
        "./templates/cosmic_onboarding.html"
    ]
    
    # Use the path specified as an argument, if provided
    if len(sys.argv) > 1:
        potential_paths = [sys.argv[1]]
    
    success = False
    for path in potential_paths:
        if update_fetch_calls(path):
            success = True
            logger.info(f"Successfully updated {path}")
    
    if not success:
        logger.error("Failed to update any files")
        sys.exit(1)
    
    logger.info("All fetch calls updated successfully")
    sys.exit(0)