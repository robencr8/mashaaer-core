#!/bin/bash

# Make the comprehensive test executable
chmod +x comprehensive_test.py

# Start the server for testing
echo "Starting the Mashaaer application server..."
gunicorn --bind 0.0.0.0:5000 main:app &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Run the tests
echo "Running comprehensive tests..."
python comprehensive_test.py

# Clean up
echo "Stopping server..."
kill $SERVER_PID

echo "Testing completed!"
