#!/bin/bash
echo "Stopping any existing Python servers..."
pkill -f python || true
echo "Starting minimal HTTP server..."
python minimal_server.py
