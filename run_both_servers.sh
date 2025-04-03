#!/bin/bash

# Start both servers in parallel
echo "Starting main application on port 5000..."
# Uses gunicorn for the main application (already configured in workflow)
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app &
MAIN_PID=$!

echo "Starting standalone minimal server on port 5001..."
# Use python directly for the standalone server
python standalone_minimal_server.py &
MINIMAL_PID=$!

# Function to handle script termination
function cleanup {
  echo "Stopping servers..."
  kill $MAIN_PID 2>/dev/null
  kill $MINIMAL_PID 2>/dev/null
  exit
}

# Set up trap to catch termination signal
trap cleanup SIGINT SIGTERM

# Keep script running
echo "Both servers are running. Press Ctrl+C to stop."
echo "Main application: http://0.0.0.0:5000"
echo "Standalone minimal server: http://0.0.0.0:5001"
wait