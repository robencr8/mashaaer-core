#!/bin/bash

# This script fixes the ElevenLabs API key issue by directly setting it in the .env file
# Usage: ./fix_elevenlabs.sh YOUR_API_KEY_HERE

if [ -z "$1" ]; then
  echo "Error: No API key provided"
  echo "Usage: ./fix_elevenlabs.sh YOUR_API_KEY_HERE"
  exit 1
fi

API_KEY=$1

# Replace the variable placeholder with the actual key in .env
sed -i "s|ELEVENLABS_API_KEY=\${ELEVENLABS_API_KEY}|ELEVENLABS_API_KEY=$API_KEY|g" .env

# Log the change (without showing the actual key)
echo "Updated .env file with direct ElevenLabs API key"
echo "Key length: ${#API_KEY} characters"

# Also export it to the current environment
export ELEVENLABS_API_KEY=$API_KEY
echo "Exported API key to environment"

echo "Fix complete. Please restart the application for changes to take effect."