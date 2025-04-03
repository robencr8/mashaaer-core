# Feedback Tool Integration Guide

This documentation provides comprehensive guidance for diagnosing and resolving connectivity issues with the web application feedback tool in the Mashaaer Feelings application.

## Table of Contents

1. [Introduction](#introduction)
2. [CORS Configuration](#cors-configuration)
3. [Diagnostic Endpoints](#diagnostic-endpoints)
4. [Testing Tools](#testing-tools)
5. [Troubleshooting](#troubleshooting)
6. [Implementation Details](#implementation-details)

## Introduction

The Mashaaer Feelings application includes specialized endpoints and configuration to ensure compatibility with the Replit web application feedback tool. This document describes the approaches taken to diagnose and resolve connectivity issues.

## CORS Configuration

Cross-Origin Resource Sharing (CORS) is a crucial aspect of ensuring the feedback tool can communicate with our application. The application implements several CORS-related features:

### Key CORS Headers

```
Access-Control-Allow-Origin: <origin> 
Access-Control-Allow-Methods: GET, POST, OPTIONS, HEAD
Access-Control-Allow-Headers: *
Access-Control-Max-Age: 86400
Access-Control-Allow-Credentials: true (when needed)
```

### Environment Variables

- `FEEDBACK_TOOL_ORIGIN`: Contains the exact origin of the feedback tool to enable precise CORS control

### Implementation

CORS is implemented at multiple levels:

1. **Global CORS**: Applied using Flask-CORS for application-wide protection
2. **Endpoint-specific CORS**: Custom headers applied to specific endpoints
3. **Feedback Tool Endpoints**: Specialized endpoints with maximum CORS compatibility

## Diagnostic Endpoints

The following endpoints are specifically designed for diagnosing feedback tool connectivity:

### `/feedback-tool-endpoint` (GET, OPTIONS)

Ultra-minimal endpoint returning plain text for maximum compatibility.

**Sample Response**:
```
OK - Mashaaer Feelings server is running and accessible.
```

### `/api/feedback-tool-status` (GET, OPTIONS)

Detailed diagnostic endpoint returning comprehensive information about the server and request.

**Sample Response**:
```json
{
  "status": "online",
  "message": "Server is accessible by the feedback tool",
  "timestamp": "2025-04-03T23:32:36.177Z",
  "replit_info": {
    "domain": "b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev",
    "full_domain": "https://b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev/",
    "worf_domain": "workspace--robenedwan.repl.co",
    "slug": "workspace",
    "owner": "robenedwan",
    "repl_id": "b846eda6-3902-424b-86a3-00b49b2e7d19",
    "feedback_tool_origin": "https://b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev"
  },
  "request": {
    "method": "GET",
    "path": "/api/feedback-tool-status",
    "url": "https://b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev/api/feedback-tool-status",
    "origin": "https://b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev",
    "remote_addr": "172.31.128.40",
    "headers": {
      "Host": "b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev",
      "User-Agent": "Mozilla/5.0 (compatible)",
      "Accept": "*/*",
      "Origin": "https://b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev"
    },
    "args": {},
    "data": null
  },
  "env_vars": {
    "REPL_SLUG": "workspace",
    "REPL_OWNER": "robenedwan",
    "REPL_ID": "b846eda6-3902-424b-86a3-00b49b2e7d19",
    "PORT": "5000",
    "REPLIT_DEPLOYMENT_ID": "Not set"
  }
}
```

### `/api/minimal` (GET, OPTIONS)

Minimal endpoint returning plain text with basic CORS headers.

**Sample Response**:
```
Server is running. Status: OK. Timestamp: 2025-04-03T23:32:36.177Z
```

### `/api/test-cors-minimal` (GET, POST, OPTIONS)

Test endpoint with detailed CORS configuration and response information.

**Sample Response**:
```json
{
  "message": "CORS test successful",
  "method": "GET",
  "request_origin": "https://b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev",
  "timestamp": "2025-04-03T23:32:36.177Z"
}
```

### `/api/debug-request` (GET, POST, OPTIONS)

Advanced diagnostic endpoint that returns complete details about the request, including all headers, environment variables, and request properties.

## Testing Tools

Several testing tools are available to diagnose connectivity issues:

### `/feedback-comprehensive-test`

Advanced test page with:
- Multiple endpoint tests
- Custom request construction
- Header and body configuration
- Detailed request/response analysis
- Browser and network diagnostics

### `test_server_connectivity.py`

Standalone Python script to test connectivity from outside the browser context.

**Usage**:
```bash
python test_server_connectivity.py [base_url]
```

### `standalone_minimal_server.py`

Isolated minimal server for testing if CORS issues are related to the main application configuration.

**Usage**:
```bash
python standalone_minimal_server.py [port]
```

## Troubleshooting

Common issues and their solutions:

### CORS Errors

1. **Missing Origin Header**: Ensure the `Origin` header is correctly echoed in the `Access-Control-Allow-Origin` response header
2. **Invalid CORS Configuration**: Use the diagnostic tools to verify all required CORS headers are present
3. **Preflight Failures**: Test OPTIONS requests to ensure they return proper CORS headers

### Network Connectivity

1. **Blocked Requests**: Check for network firewalls or proxy issues
2. **HTTPS Mixed Content**: Ensure all resources use HTTPS when the main page is served over HTTPS
3. **Replit-Specific Issues**: Verify the application is accessible from the Replit domain

### Environment Configuration

1. **Port Configuration**: Verify the server is listening on the correct port (typically 5000)
2. **Host Binding**: Ensure the server is bound to `0.0.0.0` to accept external connections
3. **Environment Variables**: Verify `FEEDBACK_TOOL_ORIGIN` is correctly set

## Implementation Details

### Core Files

1. **main.py**: Contains the primary feedback tool endpoint implementation
2. **routes_feedback_tool.py**: Contains specialized feedback tool route implementations
3. **static/feedback_tool_test.html**: Advanced testing interface

### Key Code Implementations

#### Feedback Tool Endpoint

```python
@app.route('/feedback-tool-endpoint', methods=['GET', 'OPTIONS'])
def feedback_tool_endpoint():
    """Endpoint optimized for the web application feedback tool with all CORS headers"""
    # Log all request details to help diagnose issues
    origin = request.headers.get('Origin', FEEDBACK_TOOL_ORIGIN or '*')
    logger.info(f"⭐ Feedback tool endpoint accessed from origin: {origin}")
    logger.info(f"⭐ Request headers: {dict(request.headers)}")
    
    # For OPTIONS preflight requests
    if request.method == 'OPTIONS':
        logger.info(f"⭐ Handling OPTIONS preflight for feedback tool endpoint from {origin}")
        response = make_response()
        
        # Maximum permissiveness for CORS headers
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, HEAD'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Max-Age'] = '86400'
        
        return response
    
    # For GET requests - Ultra simple text response for maximum compatibility
    response = make_response("OK - Mashaaer Feelings server is running and accessible.")
    
    # Set Content-Type to plain text for maximum compatibility
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    
    # Maximum permissiveness for CORS headers in the response
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS, HEAD'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Max-Age'] = '86400'
    
    logger.info(f"⭐ Response headers: {dict(response.headers)}")
    return response
```

#### Feedback Tool Status Endpoint

```python
@feedback_tool_bp.route('/api/feedback-tool-status', methods=['GET', 'OPTIONS'])
def feedback_tool_status():
    """Status endpoint optimized for feedback tool with explicit CORS headers and request details."""
    origin = request.headers.get('Origin', '*')  # Echo the Origin or allow all
    logger.info(f"Feedback tool status endpoint accessed from origin: {origin}")
    logger.debug(f"Request Headers: {dict(request.headers)}")  # Log all request headers

    # For OPTIONS preflight requests
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight for feedback tool status endpoint from {origin}")
        response = make_response()
        
        # Maximum permissiveness for CORS headers
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, HEAD'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Max-Age'] = '86400'
        
        return response
    
    response_data = {
        'status': 'online',
        'message': 'Server is accessible by the feedback tool',
        'timestamp': datetime.now().isoformat(),
        'replit_info': {
            'domain': request.host,  # The host the server is running on
            'full_domain': request.host_url,
            'worf_domain': f"{os.environ.get('REPL_SLUG', 'unknown')}--{os.environ.get('REPL_OWNER', 'unknown')}.repl.co",
            'slug': os.environ.get('REPL_SLUG', 'unknown'),
            'owner': os.environ.get('REPL_OWNER', 'unknown'),
            'repl_id': os.environ.get('REPL_ID', 'unknown'),
            'feedback_tool_origin': os.environ.get('FEEDBACK_TOOL_ORIGIN', 'Not set')
        },
        'request': {
            'method': request.method,
            'path': request.path,
            'url': request.url,
            'origin': origin,
            'remote_addr': request.remote_addr,
            'headers': {k: v for k, v in request.headers.items()},
            'args': {k: v for k, v in request.args.items()},
            'data': request.get_data(as_text=True) if request.data else None
        },
        'env_vars': {
            'REPL_SLUG': os.environ.get('REPL_SLUG', 'Not set'),
            'REPL_OWNER': os.environ.get('REPL_OWNER', 'Not set'),
            'REPL_ID': os.environ.get('REPL_ID', 'Not set'),
            'PORT': os.environ.get('PORT', '5000'),
            'REPLIT_DEPLOYMENT_ID': os.environ.get('REPLIT_DEPLOYMENT_ID', 'Not set'),
        }
    }

    response = jsonify(response_data)
    
    # Maximum permissiveness for CORS headers in the response
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS, HEAD'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Content-Length, Authorization'
    response.headers['Access-Control-Max-Age'] = '86400'
    
    logger.debug(f"Response Headers: {dict(response.headers)}")
    return response
```