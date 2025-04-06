#!/bin/bash

# Mashaaer Feelings Comprehensive Test Script
# This script runs tests against different environments of the Mashaaer application

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}=================================================${NC}"
echo -e "${PURPLE}   Mashaaer Feelings Comprehensive Test Script   ${NC}"
echo -e "${PURPLE}=================================================${NC}"

# Check if the application is running
echo -e "\n${BLUE}Checking if the application server is running...${NC}"
if curl -s http://localhost:5000/ > /dev/null; then
    echo -e "${GREEN}✓ Application server is running on port 5000${NC}"
else
    echo -e "${RED}✗ Application server is not running on port 5000${NC}"
    echo -e "${YELLOW}Starting the application server...${NC}"
    
    # Try to start the server
    echo -e "${YELLOW}Press Ctrl+C to stop tests when done.${NC}"
    gnome-terminal -- bash -c "gunicorn --bind 0.0.0.0:5000 main:app" &
    
    # Wait for server to start
    echo -e "${YELLOW}Waiting for server to start...${NC}"
    for i in {1..10}; do
        if curl -s http://localhost:5000/ > /dev/null; then
            echo -e "${GREEN}✓ Application server started successfully${NC}"
            break
        fi
        if [ $i -eq 10 ]; then
            echo -e "${RED}✗ Failed to start application server${NC}"
            echo -e "${RED}Please start the application server manually and try again${NC}"
            exit 1
        fi
        echo -n "."
        sleep 1
    done
    echo ""
fi

# Create test results directory
RESULTS_DIR="test_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p $RESULTS_DIR
echo -e "${BLUE}Test results will be saved in: ${RESULTS_DIR}${NC}"

# Test local environment
echo -e "\n${CYAN}=============== Testing Local Environment ===============${NC}"
echo -e "${YELLOW}Testing on: http://localhost:5000${NC}"
python comprehensive_test.py > "${RESULTS_DIR}/local_test.log" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Local tests completed${NC}"
else
    echo -e "${RED}✗ Local tests failed${NC}"
fi
echo -e "${BLUE}Test log: ${RESULTS_DIR}/local_test.log${NC}"

# Test API endpoints one by one
echo -e "\n${CYAN}=============== Testing API Endpoints ===============${NC}"

# Function to test an API endpoint
test_endpoint() {
    local endpoint=$1
    local method=$2
    local data=$3
    local name=$4
    
    echo -e "${YELLOW}Testing: ${name} (${method} ${endpoint})${NC}"
    
    if [ "$method" == "GET" ]; then
        result=$(curl -s -o "${RESULTS_DIR}/${name// /_}.json" -w "%{http_code}" ${endpoint})
    else
        result=$(curl -s -X ${method} -H "Content-Type: application/json" -d "${data}" -o "${RESULTS_DIR}/${name// /_}.json" -w "%{http_code}" ${endpoint})
    fi
    
    if [[ $result == 2* ]]; then
        echo -e "${GREEN}✓ ${name}: Success (${result})${NC}"
    else
        echo -e "${RED}✗ ${name}: Failed (${result})${NC}"
    fi
}

# Test basic API endpoints
test_endpoint "http://localhost:5000/direct-feedback" "GET" "" "Direct Feedback Page"
test_endpoint "http://localhost:5000/api/analyze-emotion" "POST" '{"text":"I feel really happy today!"}' "Emotion Analysis API"
test_endpoint "http://localhost:5000/api/chat" "POST" '{"message":"I feel alone today","emotion":"sad","user_id":"test_user","lang":"en"}' "Chat API"
test_endpoint "http://localhost:5000/api/recommendations/contextual" "POST" '{"emotion":"sad","user_id":"test_user","lang":"en","context":{"time_of_day":"evening","day_of_week":"monday","season":"winter"}}' "Contextual Recommendations API"
test_endpoint "http://localhost:5000/api/cosmic-sound" "POST" '{"emotion":"happy","action":"info"}' "Cosmic Sound API"
test_endpoint "http://localhost:5000/api/play-cosmic-sound/happy" "GET" "" "Cosmic Sound File API"
test_endpoint "http://localhost:5000/api/translate-idiom" "POST" '{"text":"break a leg","source_lang":"en","target_lang":"ar"}' "Idiom Translation API"

# Test browser connectivity
echo -e "\n${CYAN}=============== Testing Browser Connectivity ===============${NC}"
echo -e "${YELLOW}Creating a simple test HTML file...${NC}"

cat > "${RESULTS_DIR}/browser_test.html" << EOL
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mashaaer Browser Connectivity Test</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .success { color: green; }
        .error { color: red; }
        #results { margin: 20px 0; padding: 10px; border: 1px solid #ddd; background: #f5f5f5; }
    </style>
</head>
<body>
    <h1>Mashaaer Browser Connectivity Test</h1>
    <p>This page tests connectivity to the Mashaaer backend from a browser environment.</p>
    <button id="testButton">Run Test</button>
    <div id="results">Results will appear here...</div>
    
    <script>
        document.getElementById('testButton').addEventListener('click', async function() {
            const results = document.getElementById('results');
            results.innerHTML = '<p>Running tests...</p>';
            
            let testResults = [];
            
            // Function to test an endpoint
            async function testEndpoint(name, url, method = 'GET', body = null) {
                try {
                    const fetchOptions = {
                        method: method,
                        headers: method !== 'GET' ? {'Content-Type': 'application/json'} : {}
                    };
                    
                    if (body) {
                        fetchOptions.body = JSON.stringify(body);
                    }
                    
                    const startTime = performance.now();
                    const response = await fetch(url, fetchOptions);
                    const endTime = performance.now();
                    const responseTime = Math.round(endTime - startTime);
                    
                    if (response.ok) {
                        return {
                            name: name,
                            success: true,
                            status: response.status,
                            responseTime: responseTime
                        };
                    } else {
                        return {
                            name: name,
                            success: false,
                            status: response.status,
                            error: response.statusText,
                            responseTime: responseTime
                        };
                    }
                } catch (error) {
                    return {
                        name: name,
                        success: false,
                        error: error.message
                    };
                }
            }
            
            // Run tests
            testResults.push(await testEndpoint('Server Connection', '/'));
            testResults.push(await testEndpoint('Direct Feedback', '/direct-feedback'));
            testResults.push(await testEndpoint('Emotion Analysis API', '/api/analyze-emotion', 'POST', {
                text: 'I feel happy today!'
            }));
            testResults.push(await testEndpoint('Chat API', '/api/chat', 'POST', {
                message: 'Hello, how are you?',
                emotion: 'neutral',
                user_id: 'browser_tester',
                lang: 'en'
            }));
            
            // Display results
            let resultsHtml = '<h2>Test Results</h2>';
            let passCount = testResults.filter(result => result.success).length;
            
            resultsHtml += `<p>${passCount} of ${testResults.length} tests passed</p>`;
            resultsHtml += '<ul>';
            
            testResults.forEach(result => {
                const statusClass = result.success ? 'success' : 'error';
                const statusSymbol = result.success ? '✓' : '✗';
                
                resultsHtml += `<li class="${statusClass}">${statusSymbol} ${result.name}: `;
                
                if (result.success) {
                    resultsHtml += `Status ${result.status}, Response time: ${result.responseTime}ms`;
                } else {
                    resultsHtml += `Failed - ${result.error || result.status}`;
                }
                
                resultsHtml += '</li>';
            });
            
            resultsHtml += '</ul>';
            results.innerHTML = resultsHtml;
        });
    </script>
</body>
</html>
EOL

echo -e "${GREEN}✓ Created browser test at: ${RESULTS_DIR}/browser_test.html${NC}"
echo -e "${YELLOW}You can open this file in a browser to test connectivity${NC}"

# Test Summary
echo -e "\n${CYAN}=============== Test Summary ===============${NC}"
echo -e "${BLUE}All test results are saved in: ${RESULTS_DIR}${NC}"
echo -e "${BLUE}To view detailed results, check the JSON files and logs in that directory${NC}"
echo -e "${GREEN}To test from a browser environment, open: ${RESULTS_DIR}/browser_test.html${NC}"

echo -e "\n${PURPLE}=================================================${NC}"
echo -e "${PURPLE}   Mashaaer Feelings Testing Completed   ${NC}"
echo -e "${PURPLE}=================================================${NC}"