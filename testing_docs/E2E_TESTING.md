# End-to-End Testing for Mashaaer Feelings Application

This document provides instructions for running the end-to-end (E2E) tests for the Mashaaer Feelings application.

## Overview

The E2E tests verify that the entire application functions correctly by simulating real user interactions. These tests cover:

- API endpoints functionality
- Emotion analysis
- Chat interactions
- Rule management
- Cosmic sound features
- Multilingual support (English and Arabic)

## Test Files

The repository includes the following test files:

1. `e2e_test.py` - Comprehensive end-to-end tests for all application features
2. `simple_e2e_test.py` - Simplified tests for basic API functionality
3. `simple_test_run.sh` - Script to run both test files in sequence

## Prerequisites

Before running the tests, ensure you have the following:

- Python 3.7 or higher installed
- Required Python packages: `requests`, `pytest`
- The application running (either locally or deployed)

## Running the Tests

### Option 1: Using the Test Script

The simplest way to run the tests is using the provided script:

```bash
# Make the script executable if needed
chmod +x simple_test_run.sh

# Run the tests
./simple_test_run.sh
```

This script will:
1. Run the simple E2E tests first
2. If those pass, run the comprehensive E2E tests

### Option 2: Running Individual Test Files

You can also run the test files individually:

```bash
# Run the simple E2E tests
python simple_e2e_test.py [base_url]

# Run the comprehensive E2E tests
python e2e_test.py [base_url]
```

Where `[base_url]` is optional and defaults to `http://localhost:5000`.

### Option 3: Running with a Deployed Application

To test against a deployed application instead of a local one:

```bash
# For simple tests
python simple_e2e_test.py https://your-deployed-app.example.com

# For comprehensive tests
python e2e_test.py https://your-deployed-app.example.com
```

## Test Results

The tests will output detailed results to the console, including:

- Which endpoints were tested
- Whether each test passed or failed
- Detailed error messages for failed tests
- A summary of all test results

A non-zero exit code indicates test failure, which can be used in CI/CD pipelines.

## Troubleshooting

If the tests fail, check the following:

1. Ensure the application is running and accessible
2. Check that the correct base URL is being used
3. Verify that all required dependencies are installed
4. Look for specific error messages in the test output
5. Check the application logs for any server-side errors

## Advanced Usage

### Running in CI/CD Pipeline

The tests can be integrated into a CI/CD pipeline using the following pattern:

```yaml
test:
  script:
    - pip install -r requirements.txt
    - gunicorn --daemon --bind 0.0.0.0:5000 main:app
    - sleep 5  # Give the server time to start
    - python e2e_test.py
    - pkill gunicorn
```

### Adding New Tests

To add new tests to the E2E test suite:

1. Identify a feature or endpoint that needs testing
2. Add a new test function to `e2e_test.py` following the existing pattern
3. Add the new test to the `tests` list in the `run_all_tests` function
4. Run the tests to verify the new test works correctly

## Maintaining Tests

As the application evolves, the tests should be updated to reflect new features and changes:

1. Review tests after significant application changes
2. Update expected responses and test cases as needed
3. Remove tests for deprecated features
4. Add tests for new features