# Known Issues

## Web Application Feedback Tool Integration

### Issue: Web Server Reported as Unreachable

**Description:**  
The web application feedback tool persistently reports that the web server is unreachable despite the server being fully functional and accessible via other means.

**Verification Steps Performed:**
1. Direct browser access to all endpoints consistently works
2. curl commands successfully connect to all endpoints
3. Server logs confirm that requests are being processed
4. Root-level health checks return expected responses
5. Explicit CORS headers are properly configured
6. Multiple test pages with varying levels of complexity all work via direct access

**Potential Causes:**
1. CORS configuration incompatibility specific to the feedback tool
2. Network routing issues between the feedback tool and the server
3. Potential port access restrictions in the feedback tool's environment
4. Specific HTTP header requirements not documented

**Workarounds:**
1. **Use Direct Browser Testing:**  
   Use direct browser access to test application functionality instead of relying on the feedback tool.

2. **Use curl for API Testing:**  
   Test API endpoints using curl commands with appropriate headers.

3. **Use the Standalone Minimal Server:**  
   The `standalone_minimal_server.py` script provides an ultra-minimal Flask server with no dependencies that can be used to isolate and test basic connectivity.

4. **Diagnostic Endpoints and Tools:**  
   - Use `/health`, `/api/ping`, and other minimal endpoints to verify basic connectivity
   - Access `/enhanced-diagnostic` for a comprehensive testing tool with connectivity tests, CORS diagnostics, and API testing capabilities
   - Use `/diagnostic` or `/diagnostic-static` for basic diagnostics
   - Access `/api/debug-request` for detailed request information with headers and environment data

## CORS Configuration

### Issue: OPTIONS Preflight Requests Not Working as Expected

**Description:**  
In some cases, CORS preflight OPTIONS requests may not be handled correctly despite proper configuration.

**Workaround:**  
Add explicit handling for OPTIONS requests to all relevant routes with proper CORS headers.

```python
@app.route('/api/your-endpoint', methods=['GET', 'POST', 'OPTIONS'])
def your_endpoint():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'  # Or specific origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response
    
    # Normal handler code here
```

## ElevenLabs API Integration

### Issue: ElevenLabs API Occasionally Returns 429 (Too Many Requests)

**Description:**  
When using the ElevenLabs API for text-to-speech, occasionally requests may fail with a 429 status code indicating rate limiting.

**Workaround:**  
The system automatically falls back to Google TTS when ElevenLabs is unavailable or returns errors.

## Mobile API Routes

### Issue: Duplicate Route Definitions

**Description:**  
Some API routes are defined in multiple files, which can lead to confusion about which implementation is being used.

**Workaround:**  
Use the `api_routes.py` file as the authoritative source for API endpoint definitions. Mobile-specific routes should be exclusively in `mobile_api_routes.py`.

## Web Server Stability

### Issue: Occasional Web Server Unavailability

**Description:**  
The web server may occasionally become unresponsive, particularly under high load or after extended periods of inactivity.

**Workaround:**  
1. Restart the application workflow
2. Use the health check endpoint to monitor server status
3. Implement a watchdog script to automatically restart the server if it becomes unresponsive
