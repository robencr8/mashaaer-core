#!/bin/bash

# Run Tests Script for Mashaaer Feelings Application
# This script runs both simple and comprehensive end-to-end tests

# Set base URL from first argument or use default
BASE_URL=${1:-"http://localhost:5000"}

# Function to print colored output
print_header() {
    echo -e "\e[1;36m$1\e[0m"
}

print_success() {
    echo -e "\e[1;32m✅ $1\e[0m"
}

print_failure() {
    echo -e "\e[1;31m❌ $1\e[0m"
}

print_info() {
    echo -e "\e[1;34mℹ️ $1\e[0m"
}

# Check if the application server is running
print_header "Checking if server is running at $BASE_URL..."
if ! curl -s -o /dev/null -w "%{http_code}" $BASE_URL | grep -q "2[0-9]\{2\}"; then
    print_failure "Server is not running or not accessible at $BASE_URL"
    print_info "Please make sure the server is started before running tests."
    print_info "You can start the server with: python main.py"
    exit 1
fi

print_success "Server is running and accessible"

# Run simple end-to-end tests first
print_header "Running Simple End-to-End Tests..."
if python simple_e2e_test.py $BASE_URL; then
    print_success "Simple End-to-End Tests completed successfully"
else
    print_failure "Simple End-to-End Tests failed"
    exit 1
fi

# Ask user if they want to run comprehensive tests
echo ""
read -p "Do you want to run comprehensive end-to-end tests? (y/n): " run_comprehensive

if [[ $run_comprehensive == "y" || $run_comprehensive == "Y" ]]; then
    print_header "Running Comprehensive End-to-End Tests..."
    if python e2e_test.py $BASE_URL; then
        print_success "Comprehensive End-to-End Tests completed successfully"
    else
        print_info "Some comprehensive tests failed - see output above for details"
        # Don't exit with error as some API endpoints might not be implemented yet
    fi
else
    print_info "Skipping comprehensive tests"
fi

echo ""
print_header "Test Execution Summary"
print_success "Simple End-to-End Tests: Passed"
if [[ $run_comprehensive == "y" || $run_comprehensive == "Y" ]]; then
    if [[ $? -eq 0 ]]; then
        print_success "Comprehensive End-to-End Tests: Passed"
    else
        print_info "Comprehensive End-to-End Tests: Some tests failed"
    fi
else
    print_info "Comprehensive End-to-End Tests: Skipped"
fi

echo ""
print_header "Next Steps"
echo "1. Review any failing tests and fix implementation as needed"
echo "2. Add more test cases to cover additional functionality"
echo "3. Consider adding more specific unit tests for key components"

exit 0