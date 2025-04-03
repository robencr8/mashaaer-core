"""
Ultra-minimal Flask server for CORS testing
This is a standalone server that is stripped to the absolute minimum needed for CORS testing
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import traceback
from datetime import datetime

# Configure extensive logging for CORS debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Keep CORS permissive for this minimal test (INSECURE for production)
CORS(app, origins="*", methods=['GET', 'POST', 'OPTIONS'], allow_headers='*', supports_credentials=True)

@app.route('/api/test-cors-minimal', methods=['GET', 'POST', 'OPTIONS'])
def cors_test_minimal():
    """A minimal endpoint to test CORS."""
    logger.info(f"Received request to /api/test-cors-minimal: {request.method} {request.url}")

    try:
        # Log request details
        logger.debug(f"Request Headers: {dict(request.headers)}")
        if request.method == 'POST' and request.is_json:
            try:
                logger.debug(f"Request Body: {request.get_json()}")
            except Exception as e:
                logger.debug(f"Could not parse request body as JSON: {e}")

        # Echo the Origin header if present, otherwise, allow all
        origin = request.headers.get('Origin')
        response_headers = {
            'Access-Control-Allow-Origin': origin if origin else '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': request.headers.get('Access-Control-Request-Headers', 'Content-Type, Authorization, X-Requested-With'),
            'Access-Control-Allow-Credentials': 'true'  # Only if absolutely necessary
        }

        # For OPTIONS requests (preflight)
        if request.method == 'OPTIONS':
            logger.info(f"Handling OPTIONS preflight request from {origin}")
            response = jsonify({})
            response.headers.extend(response_headers)
            response.status_code = 200
            logger.debug(f"OPTIONS Response Headers: {dict(response.headers)}")
            return response
        
        # Construct a minimal response with the echoed Origin
        response_data = {
            'message': 'CORS test successful',
            'method': request.method,
            'request_origin': origin,
            'request_headers': dict(request.headers),
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
                logger.error(traceback.format_exc())
        
        response = jsonify(response_data)
        response.headers.extend(response_headers)
        response.status_code = 200
        logger.debug(f"Response Headers: {dict(response.headers)}")
        return response

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        logger.error(traceback.format_exc())  # Log the full traceback
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

@app.route('/')
def index():
    """Serve a simple HTML page for testing CORS"""
    try:
        logger.info("Root route accessed")
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
            <p>Testing CORS...</p>
            <button id="getButton">Test CORS (GET)</button>
            <button id="postButton">Test CORS (POST)</button>
            <div id="requestInfo" style="margin-top: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 4px;"></div>
            <div id="result"></div>
            <script>
                const resultDiv = document.getElementById('result');
                const requestInfoDiv = document.getElementById('requestInfo');
                const getButton = document.getElementById('getButton');
                const postButton = document.getElementById('postButton');

                function displayResult(data, error = false) {
                    resultDiv.innerHTML = `<h3>Response:</h3><pre class="${error ? 'error' : 'success'}">${data}</pre>`;
                }
                
                function displayRequestInfo(method, url) {
                    requestInfoDiv.innerHTML = `<h3>Request:</h3><pre>Method: ${method}\\nURL: ${url}\\nOrigin: ${window.location.origin}</pre>`;
                }

                getButton.addEventListener('click', () => {
                    const url = '/api/test-cors-minimal';
                    displayRequestInfo('GET', url);
                    displayResult('Sending GET request...');
                    
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
                            displayResult(JSON.stringify(data, null, 2));
                            console.log('Success:', data);
                        })
                        .catch(error => {
                            displayResult(`Error: ${error.message}`, true);
                            console.error('GET Fetch error:', error);
                        });
                });

                postButton.addEventListener('click', () => {
                    const url = '/api/test-cors-minimal';
                    displayRequestInfo('POST', url);
                    displayResult('Sending POST request...');
                    
                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ data: 'test', timestamp: new Date().toISOString() })
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
                            displayResult(JSON.stringify(data, null, 2));
                            console.log('Success:', data);
                        })
                        .catch(error => {
                            displayResult(`Error: ${error.message}`, true);
                            console.error('POST Fetch error:', error);
                        });
                });
            </script>
        </body>
        </html>
        '''
    except Exception as e:
        logger.error(f"Error serving index page: {e}")
        logger.error(traceback.format_exc())
        return "An error occurred", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Use port 5001 by default to avoid conflicts
    try:
        logger.info(f"Starting ultra-minimal server on port {port}")
        app.run(debug=True, host='0.0.0.0', port=port)  # Listen on all interfaces
    except Exception as e:
        logger.critical(f"Error starting Flask app: {e}")
        logger.critical(traceback.format_exc())