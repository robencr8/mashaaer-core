# API Diagnostic Endpoints

This document outlines the specialized diagnostic endpoints created to troubleshoot CORS and Replit Feedback Tool compatibility issues.

## Diagnostic URLs

### 1. Main Flask Application (Port 5000)

- **Health Check**: `/health`
  - Returns basic server health information
  - Example: `curl http://localhost:5000/health`

- **Feedback Tool Test**: `/replit-feedback-test`
  - Designed specifically for testing Replit feedback tool compatibility
  - Example: `curl http://localhost:5000/replit-feedback-test`

- **CORS Debug Tool**: `/cors-debug`
  - Interactive tool to test various CORS configurations
  - Navigate to: http://localhost:5000/cors-debug

- **API Status**: `/api/status`
  - Returns API service status with CORS headers
  - Example: `curl http://localhost:5000/api/status`

### 2. Simple Server (Port 5001)

This is a minimal Flask server designed for maximum compatibility:
- **Root**: `http://localhost:5001/`
- **Health**: `http://localhost:5001/health`

### 3. Micro HTTP Server (Port 5002)

This is a bare-bones server using Python's standard library:
- **Root**: `http://localhost:5002/`
- **Health**: `http://localhost:5002/health`

## CORS Configuration

All endpoints include the following CORS headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

## Troubleshooting Steps

1. **Browser Console**: Check for CORS-related errors in the console
2. **Network Tab**: Analyze requests/responses for CORS headers
3. **Test Simple Endpoints**: Start with `/health` before testing complex endpoints
4. **Try Alternative Servers**: If main server fails, try the simple or micro server
5. **Verify Client Origin**: Ensure the origin in the request matches allowed origins

## Common CORS Errors

- **No 'Access-Control-Allow-Origin' header**: Server not including CORS headers
- **Method not allowed**: Missing proper OPTIONS preflight handler
- **Credentials not supported with wildcard origin**: Using both credentials and wildcard ('*')
- **Preflight response invalid**: OPTIONS request returned non-2xx status

## Request Status Codes

- **200**: Success
- **204**: Success with no content (common for OPTIONS)
- **400**: Bad request
- **403**: Forbidden
- **404**: Not found
- **500**: Server error

## Further Assistance

If issues persist after trying these diagnostic endpoints, consider:
1. Reviewing server logs for additional error details
2. Using a proxy to intercept and modify requests/responses
3. Testing with different browsers or network conditions
4. Contacting Replit support for feedback tool-specific issues