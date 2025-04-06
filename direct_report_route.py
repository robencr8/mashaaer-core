"""
Direct report route for comprehensive testing and reporting

This module provides routes that can generate detailed reports about the
server's configuration, connectivity, and CORS settings.
"""
import logging
import os
import socket
import sys
import platform
import requests
from flask import Blueprint, render_template, request, jsonify, current_app

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

direct_report_bp = Blueprint('direct_report', __name__)

@direct_report_bp.route('/server-info')
def server_info():
    """Return detailed information about the server"""
    # Get network info
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = "Unable to determine IP"
    
    # Get environment info
    environment = {
        "hostname": hostname,
        "ip_address": ip_address,
        "python_version": sys.version,
        "platform": platform.platform(),
        "process_id": os.getpid(),
    }
    
    # Get Flask config info (without sensitive data)
    flask_config = {}
    for key in current_app.config:
        if not any(sensitive in key.lower() for sensitive in ['secret', 'password', 'token', 'key']):
            try:
                # Skip complex objects that can't be JSON serialized
                value = current_app.config[key]
                json_value = str(value)
                flask_config[key] = json_value
            except:
                flask_config[key] = "Unable to serialize"
    
    # Get current endpoints
    try:
        routes = []
        for rule in current_app.url_map.iter_rules():
            routes.append({
                "endpoint": rule.endpoint,
                "methods": sorted(list(rule.methods)),
                "rule": str(rule)
            })
    except Exception as e:
        routes = [{"error": str(e)}]
    
    # Return all info
    return jsonify({
        "environment": environment,
        "flask_config": flask_config,
        "routes": routes,
        "status": "ok"
    })

@direct_report_bp.route('/cors-report')
def cors_report():
    """Test CORS with various Origins and return a report"""
    base_url = request.url_root.rstrip('/')
    test_endpoints = [
        '/api/minimal',
        '/api/feedback',
        '/api/health'
    ]
    
    test_origins = [
        None,
        'http://localhost:5000',
        'https://replit.com',
        'https://example.com',
        request.headers.get('Origin', 'https://default-origin.example')
    ]
    
    results = []
    
    for endpoint in test_endpoints:
        endpoint_results = []
        for origin in test_origins:
            try:
                headers = {}
                if origin:
                    headers['Origin'] = origin
                
                # Do OPTIONS request
                options_response = requests.options(
                    f"{base_url}{endpoint}", 
                    headers=headers,
                    timeout=2
                )
                
                # Do GET request
                get_response = requests.get(
                    f"{base_url}{endpoint}", 
                    headers=headers,
                    timeout=2
                )
                
                cors_headers = {
                    key: value for key, value in options_response.headers.items()
                    if key.lower().startswith('access-control')
                }
                
                endpoint_results.append({
                    "origin": origin,
                    "options_status": options_response.status_code,
                    "get_status": get_response.status_code,
                    "cors_headers": cors_headers,
                    "success": True
                })
            except Exception as e:
                endpoint_results.append({
                    "origin": origin,
                    "error": str(e),
                    "success": False
                })
        
        results.append({
            "endpoint": endpoint,
            "tests": endpoint_results
        })
    
    return jsonify({
        "cors_tests": results,
        "status": "ok"
    })

@direct_report_bp.route('/report')
def report_page():
    """Serve a comprehensive report page with server and CORS info"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Server Report</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            .section { margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
            h2 { margin-top: 0; color: #333; }
            pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .success { color: green; }
            .error { color: red; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
    </head>
    <body>
        <h1>Mashaaer Server Report</h1>
        
        <div class="section">
            <h2>Current Origin Information</h2>
            <div id="origin-info">Loading...</div>
        </div>
        
        <div class="section">
            <h2>Server Information</h2>
            <div id="server-info">Loading...</div>
        </div>
        
        <div class="section">
            <h2>CORS Test Results</h2>
            <div id="cors-info">Loading...</div>
        </div>
        
        <div class="section">
            <h2>Direct Connection Tests</h2>
            <div id="connection-tests">
                <button onclick="testMinimal()">Test Minimal API</button>
                <button onclick="testFeedback()">Test Feedback API</button>
                <button onclick="testHealth()">Test Health API</button>
                <div id="test-results"></div>
            </div>
        </div>
        
        <script>
            // Display current origin
            document.getElementById('origin-info').innerHTML = `
                <p><strong>Window Origin:</strong> ${window.location.origin}</p>
                <p><strong>Window Location:</strong> ${window.location.href}</p>
                <p><strong>User Agent:</strong> ${navigator.userAgent}</p>
            `;
            
            // Get server info
            async function loadServerInfo() {
                try {
                    const response = await fetch('/server-info');
                    const data = await response.json();
                    
                    let routesHtml = '<h3>Available Routes</h3><table><tr><th>Endpoint</th><th>Methods</th><th>Rule</th></tr>';
                    data.routes.forEach(route => {
                        routesHtml += `<tr><td>${route.endpoint}</td><td>${route.methods.join(', ')}</td><td>${route.rule}</td></tr>`;
                    });
                    routesHtml += '</table>';
                    
                    let configHtml = '<h3>Flask Configuration</h3><pre>' + JSON.stringify(data.flask_config, null, 2) + '</pre>';
                    
                    let envHtml = '<h3>Environment</h3><pre>' + JSON.stringify(data.environment, null, 2) + '</pre>';
                    
                    document.getElementById('server-info').innerHTML = envHtml + configHtml + routesHtml;
                } catch (error) {
                    document.getElementById('server-info').innerHTML = `<p class="error">Error loading server info: ${error.message}</p>`;
                }
            }
            
            // Load CORS test results
            async function loadCorsInfo() {
                try {
                    const response = await fetch('/cors-report');
                    const data = await response.json();
                    
                    let corsHtml = '';
                    data.cors_tests.forEach(test => {
                        corsHtml += `<h3>Endpoint: ${test.endpoint}</h3><table>
                            <tr>
                                <th>Origin</th>
                                <th>OPTIONS Status</th>
                                <th>GET Status</th>
                                <th>CORS Headers</th>
                                <th>Result</th>
                            </tr>`;
                            
                        test.tests.forEach(result => {
                            const originText = result.origin || '(None)';
                            const statusText = result.success 
                                ? `<td>${result.options_status}</td><td>${result.get_status}</td>` 
                                : `<td colspan="2" class="error">${result.error}</td>`;
                                
                            const headersText = result.cors_headers 
                                ? `<pre>${JSON.stringify(result.cors_headers, null, 2)}</pre>` 
                                : 'N/A';
                                
                            const resultClass = result.success ? 'success' : 'error';
                            const resultText = result.success ? '✓ Pass' : '✗ Fail';
                            
                            corsHtml += `<tr>
                                <td>${originText}</td>
                                ${statusText}
                                <td>${headersText}</td>
                                <td class="${resultClass}">${resultText}</td>
                            </tr>`;
                        });
                        
                        corsHtml += '</table>';
                    });
                    
                    document.getElementById('cors-info').innerHTML = corsHtml;
                } catch (error) {
                    document.getElementById('cors-info').innerHTML = `<p class="error">Error loading CORS info: ${error.message}</p>`;
                }
            }
            
            // Direct API tests
            async function testEndpoint(endpoint, name) {
                const resultDiv = document.getElementById('test-results');
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    
                    const resultHtml = `
                        <div class="section">
                            <h3>${name} Test: <span class="success">Success (${response.status})</span></h3>
                            <pre>${JSON.stringify(data, null, 2)}</pre>
                        </div>
                    `;
                    resultDiv.innerHTML = resultHtml + resultDiv.innerHTML;
                } catch (error) {
                    const resultHtml = `
                        <div class="section">
                            <h3>${name} Test: <span class="error">Failed</span></h3>
                            <p class="error">${error.message}</p>
                        </div>
                    `;
                    resultDiv.innerHTML = resultHtml + resultDiv.innerHTML;
                }
            }
            
            function testMinimal() {
                testEndpoint('/api/minimal', 'Minimal API');
            }
            
            function testFeedback() {
                testEndpoint('/api/feedback', 'Feedback API');
            }
            
            function testHealth() {
                testEndpoint('/api/health', 'Health API');
            }
            
            // Load all data
            loadServerInfo();
            loadCorsInfo();
        </script>
    </body>
    </html>
    """

def init_direct_report(app):
    """Initialize the direct report module with the Flask app"""
    app.register_blueprint(direct_report_bp)
    logger.info("Direct report routes initialized")