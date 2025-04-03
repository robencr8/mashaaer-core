#!/usr/bin/env python3
"""
A more robust approach to update the fetch calls in cosmic_onboarding.html
using Python's re module for precise pattern matching and replacement.
"""
import os
import re
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def find_file_path(filename):
    """
    Find the path to the file by checking multiple possible locations.
    
    Args:
        filename: Base filename to look for
        
    Returns:
        str: Full path to the file if found, None otherwise
    """
    potential_paths = [
        filename,                    # Root directory
        f"templates/{filename}",     # Templates directory
        f"./templates/{filename}"    # Templates with explicit current directory
    ]
    
    for path in potential_paths:
        if os.path.exists(path):
            logger.info(f"Found {filename} at path: {path}")
            return path
    
    logger.error(f"Could not find {filename} in any of the expected locations")
    return None

def update_fetch_calls(filepath):
    """
    Updates fetch() calls in the given HTML file to use POST for /api/listen-for-voice.
    Uses Python's re module for precise pattern matching and replacement.
    
    Args:
        filepath: The path to the HTML file.
    
    Returns:
        bool: True if updates were successful, False otherwise
    """
    if not filepath or not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return False
    
    try:
        # Read the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # The pattern to match GET-style fetch calls for listen-for-voice
        pattern = re.compile(
            r'fetch\(\s*[\'"]\/api\/listen-for-voice\?language=[\'"]\s*\+\s*(\w+)\s*\)',
            re.MULTILINE
        )
        
        # Function to generate the replacement with the correct variable
        def replacement_func(match):
            var_name = match.group(1)  # Extract the variable name
            return f"""fetch('/api/listen-for-voice', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json'
      }},
      body: JSON.stringify({{
        language: {var_name}
      }})
    }})"""
        
        # Perform the replacement
        updated_content = pattern.sub(replacement_func, content)
        
        # Check if any changes were made
        if content == updated_content:
            logger.warning(f"No matching patterns found in {filepath}")
            return False
        
        # Create a backup of the original file
        backup_path = f"{filepath}.bak"
        if not os.path.exists(backup_path):
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Created backup at {backup_path}")
        
        # Write the updated content back to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        # Count the number of replacements made
        replacements = len(pattern.findall(content))
        logger.info(f"Successfully updated {replacements} fetch() calls in {filepath}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating {filepath}: {e}")
        return False

def main():
    """Main function to find and update the file."""
    # Get the filename from command line or use default
    filename = sys.argv[1] if len(sys.argv) > 1 else "cosmic_onboarding.html"
    
    # Find the file
    filepath = find_file_path(filename)
    if not filepath:
        sys.exit(1)
    
    # Update the fetch calls
    if update_fetch_calls(filepath):
        logger.info(f"Successfully updated {filepath}")
        sys.exit(0)
    else:
        logger.error(f"Failed to update {filepath}")
        sys.exit(1)

if __name__ == "__main__":
    main()