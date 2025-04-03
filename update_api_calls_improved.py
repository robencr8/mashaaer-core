#!/usr/bin/env python3
"""
Script to update fetch() calls in cosmic_onboarding.html to use POST method
instead of GET for the /api/listen-for-voice endpoint, using string methods.
"""
import sys
import logging

# Configure logging (optional but recommended)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def update_fetch_calls(filepath: str) -> bool:
    """
    Updates fetch() calls in the given HTML file to use POST for /api/listen-for-voice.

    Args:
        filepath: The path to the HTML file.

    Returns:
        bool: True if updates were successful, False otherwise
    """

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return False
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return False

    # String to search for
    search_string = "fetch('/api/listen-for-voice?language="
    # String to replace with
    replace_string = """fetch('/api/listen-for-voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: """

    updated_content = content.replace(search_string, replace_string)

    # Check if any replacements were made
    if content == updated_content:
        logger.info(f"No matches found in {filepath}")
        return False

    # Replace the closing parenthesis
    updated_content = updated_content.replace("})", "})})")

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        logger.info(f"Successfully updated fetch() calls in {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error writing to file {filepath}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_api_calls_improved.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]

    if not update_fetch_calls(filepath):
        sys.exit(1)

    sys.exit(0)