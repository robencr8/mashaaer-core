"""
Ultra-minimal Flask server for CORS testing
This is a standalone server that is stripped to the absolute minimum needed for CORS testing
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime

# Configure extensive logging for CORS debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Keep CORS permissive for this minimal test
CORS(app, origins="*", methods=['GET', 'POST', 'OPTIONS'], allow_headers='*', supports_credentials=True)

@app.route('/api/test-cors-minimal', methods=['GET', 'POST', 'OPTIONS'])
def cors_test_minimal():
    """A minimal endpoint to test CORS"""
    # Log the request and all headers for debugging
    origin = request.headers.get('Origin')
    logger.info(f"Received {request.method} request to /api/test-cors-minimal")
    logger.debug(f"Request Headers: {dict(request.headers)}")
    
    # For OPTIONS requests (preflight)
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight request from {origin}")
        response = jsonify({})
        
        # Explicitly set CORS headers
        response_headers = {
            'Access-Control-Allow-Origin': origin if origin else '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': request.headers.get('Access-Control-Request-Headers', 'Content-Type, Authorization, X-Requested-With'),
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': '3600'
        }
        
        # Add all headers to the response
        for key, value in response_headers.items():
            response.headers[key] = value
            
        logger.debug(f"OPTIONS Response Headers: {dict(response.headers)}")
        return response
    
    # For GET or POST requests
    response_data = {
        'message': 'CORS test successful',
        'method': request.method,
        'request_origin': origin,
        'timestamp': datetime.now().isoformat()
    }
    
    # If this is a POST request, include the posted data in the response
    if request.method == 'POST' and request.is_json:
        try:
            posted_data = request.get_json()
            response_data['received_data'] = posted_data
            logger.debug(f"Received JSON data: {posted_data}")
        except Exception as e:
            logger.error(f"Error parsing JSON data: {str(e)}")
    
    response = jsonify(response_data)
    
    # Explicitly set CORS headers
    response_headers = {
        'Access-Control-Allow-Origin': origin if origin else '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
    }
    
    # Add all headers to the response
    for key, value in response_headers.items():
        response.headers[key] = value
    
    logger.debug(f"Response Headers: {dict(response.headers)}")
    return response

@app.route('/')
def index():
    """Serve a simple HTML page for testing CORS"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ultra-Minimal CORS Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            button { padding: 10px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; margin: 10px 0; }
            #result { margin-top: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 4px; background-color: #f9f9f9; white-space: pre-wrap; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>Ultra-Minimal CORS Test</h1>
        <p>Click the buttons below to test CORS functionality with the minimal API endpoint.</p>
        
        <button id="testButton">Test CORS (GET)</button>
        <button id="testPostButton">Test CORS (POST)</button>
        
        <div>
            <h3>Network Request:</h3>
            <div id="requestInfo"></div>
        </div>
        
        <div>
            <h3>Response:</h3>
            <div id="result"></div>
        </div>
        
        <script>
            // Function to display response
            function displayResponse(data, error = false) {
                const resultDiv = document.getElementById('result');
                resultDiv.textContent = JSON.stringify(data, null, 2);
                resultDiv.className = error ? 'error' : 'success';
            }
            
            // Function to display request info
            function displayRequestInfo(method, url) {
                const requestInfoDiv = document.getElementById('requestInfo');
                requestInfoDiv.textContent = `Method: ${method}\\nURL: ${url}\\nOrigin: ${window.location.origin}`;
            }
            
            // GET request handler
            document.getElementById('testButton').addEventListener('click', () => {
                const url = '/api/test-cors-minimal';
                displayRequestInfo('GET', url);
                
                // Make the fetch request
                fetch(url)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        console.log('GET Response Headers:');
                        for (const [key, value] of response.headers.entries()) {
                            console.log(`${key}: ${value}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        displayResponse(data);
                        console.log('Success:', data);
                    })
                    .catch(error => {
                        displayResponse(`Error: ${error.message}`, true);
                        console.error('Error:', error);
                    });
            });
            
            // POST request handler
            document.getElementById('testPostButton').addEventListener('click', () => {
                const url = '/api/test-cors-minimal';
                displayRequestInfo('POST', url);
                
                // Make the fetch request
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ test: 'data', timestamp: new Date().toISOString() })
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        console.log('POST Response Headers:');
                        for (const [key, value] of response.headers.entries()) {
                            console.log(`${key}: ${value}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        displayResponse(data);
                        console.log('Success:', data);
                    })
                    .catch(error => {
                        displayResponse(`Error: ${error.message}`, true);
                        console.error('Error:', error);
                    });
            });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    logger.info("Starting ultra-minimal server on port 5000")
    app.run(debug=True, host='0.0.0.0', port=5000)