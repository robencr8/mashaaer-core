#!/usr/bin/env python3
"""
Script to update the fetch calls in cosmic_onboarding.html to use POST method
instead of GET for the /api/listen-for-voice endpoint.
"""
import re
import sys
import logging
import ast
import json

# Configure logging
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

    # Pattern to match the fetch() calls with language parameter
    pattern = re.compile(
        r"""
        fetch\(\s* # Match 'fetch(' and any whitespace
        (['"]\/api\/listen-for-voice\?language=\s*['"]\s*\+\s* # Match '/api/listen-for-voice?language=' + 
        ([a-zA-Z0-9_]+)\s* # Capture the language variable name
        (?:,\s*(\{.*?\})\s*)? # Optionally match and capture existing options object
        \s*\)           # Match closing parenthesis
        """, re.VERBOSE | re.IGNORECASE | re.MULTILINE
    )

    def replacement(match: re.Match) -> str:
        """
        Generates the replacement string for the fetch() call.
        """
        language_variable = match.group(2)
        existing_options_str = match.group(3) or '{}'
        try:
            existing_options = ast.literal_eval(existing_options_str)
        except (SyntaxError, ValueError):
            existing_options = {}  # Handle invalid options gracefully

        new_options = {
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'language': language_variable})
        }
        combined_options = {**existing_options, **new_options}  # Merge dictionaries
        return f"fetch('/api/listen-for-voice', {json.dumps(combined_options)})"

    updated_content = pattern.sub(replacement, content)

    # Check if any replacements were made
    if content == updated_content:
        logger.info(f"No matches found in {filepath}")
        return False

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        logger.info(f"Successfully updated fetch() calls in {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error writing to file {filepath}: {e}")
        return False

if __name__ == "__main__":
    # Try both potential paths for the file
    potential_paths = [
        "./cosmic_onboarding.html",
        "templates/cosmic_onboarding.html"
    ]

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