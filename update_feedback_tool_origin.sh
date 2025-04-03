#!/bin/bash
# Script to update the FEEDBACK_TOOL_ORIGIN in .env file

# Default to the standard Replit domain pattern
REPLIT_DOMAIN="https://${REPL_SLUG}.${REPL_OWNER}.repl.co"

# Check if an argument was provided
if [ -n "$1" ]; then
    NEW_ORIGIN="$1"
    echo "Setting FEEDBACK_TOOL_ORIGIN to custom value: $NEW_ORIGIN"
else
    NEW_ORIGIN="${REPLIT_DOMAIN}"
    echo "Setting FEEDBACK_TOOL_ORIGIN to default Replit domain: $NEW_ORIGIN"
fi

# Update .env file
if grep -q "FEEDBACK_TOOL_ORIGIN=" .env; then
    # Replace existing line
    sed -i "s|FEEDBACK_TOOL_ORIGIN=.*|FEEDBACK_TOOL_ORIGIN=${NEW_ORIGIN}|" .env
else
    # Add new line
    echo "FEEDBACK_TOOL_ORIGIN=${NEW_ORIGIN}" >> .env
fi

echo "Updated .env file. You'll need to restart the application for changes to take effect."
echo "Run 'source .env' to apply changes to current session."
