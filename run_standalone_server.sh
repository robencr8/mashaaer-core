#!/bin/bash
# Run the standalone minimal server for testing the web application feedback tool

echo "Starting standalone minimal server on port 3000..."
echo "This server is independent from the main application."
echo "Use Ctrl+C to stop the server."
echo ""
echo "Available endpoints:"
echo "  - Root endpoint: http://localhost:3000/"
echo "  - Health check: http://localhost:3000/health"
echo "  - API test: http://localhost:3000/api/test"
echo "  - API echo: http://localhost:3000/api/echo"
echo "  - Debug request: http://localhost:3000/api/debug-request"
echo ""
echo "Access from your browser or use curl to test:"
echo "  curl -v http://localhost:3000/health"
echo ""

python standalone_minimal_server.py
