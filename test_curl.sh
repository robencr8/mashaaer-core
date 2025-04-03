#!/bin/bash

echo "Testing server endpoints with curl from within the Replit environment"
echo "-----------------------------------------------------------------------"

echo -e "\nTesting /test endpoint:"
curl -v http://localhost:5000/test

echo -e "\n\nTesting /ultra-simple endpoint:"
curl -v http://localhost:5000/ultra-simple

echo -e "\n\nTesting /api/ping endpoint:"
curl -v http://localhost:5000/api/ping

echo -e "\n\nTesting /api/status endpoint:"
curl -v http://localhost:5000/api/status

chmod +x test_curl.sh
./test_curl.sh
