#!/bin/bash

# Simple script to run end-to-end tests against the application

# Set color variables
GREEN="\033[0;32m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${BLUE}=== Starting End-to-End Tests ===${NC}"
echo "Starting application workflow..."

# Start the application in the background using Replit workflows
echo "Running simple E2E tests..."
python simple_e2e_test.py

# Capture the exit code
RESULT=$?

if [ $RESULT -eq 0 ]; then
  echo -e "${GREEN}✅ Basic tests PASSED${NC}"
  
  # Run the more comprehensive tests if basic tests pass
  echo -e "${BLUE}Running comprehensive E2E tests...${NC}"
  python e2e_test.py
  
  FULL_RESULT=$?
  
  if [ $FULL_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ All end-to-end tests PASSED${NC}"
    exit 0
  else
    echo -e "${RED}❌ Some comprehensive tests FAILED${NC}"
    exit $FULL_RESULT
  fi
else
  echo -e "${RED}❌ Basic tests FAILED${NC}"
  exit $RESULT
fi
