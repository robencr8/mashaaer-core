#!/bin/bash

# Get the Replit URL
REPLIT_URL=$(echo $REPLIT_DOMAINS | cut -d ',' -f 1)

# Check if we can access the website
echo "Checking website at: https://$REPLIT_URL"
if curl -s -o /dev/null -w "%{http_code}" "https://$REPLIT_URL" | grep -q "200"; then
  echo "Website is accessible!"
else
  echo "Website is not accessible via Replit URL"
fi
