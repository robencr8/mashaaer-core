# Feedback Tool Integration Guide

## Overview

This document provides information about integrating the web application feedback tool with your Mashaaer application. It includes troubleshooting steps, diagnostic tools, and best practices for resolving connectivity issues.

## Diagnostic Tools

### Enhanced Diagnostic Tool

The enhanced diagnostic tool provides comprehensive testing capabilities specifically designed for troubleshooting web application feedback tool integration issues. Access it at `/enhanced-diagnostic`.

**Features:**
- **Connectivity Tests:** Verify server accessibility through multiple endpoints
- **CORS Diagnostics:** Test and analyze CORS configuration with detailed header inspection
- **API Tests:** Test specific API endpoints with custom parameters
- **Environment Information:** View browser and network information
- **Troubleshooting Resources:** Access guidance for common issues

### Additional Diagnostic Endpoints

The application provides several specialized diagnostic endpoints to help isolate connectivity issues:

| Endpoint | Description | Response Type |
|----------|-------------|---------------|
| `/health` | Basic health check at root level | Text |
| `/api/ping` | JSON response with timestamp | JSON |
| `/api/minimal` | Minimal text response with CORS headers | Text |
| `/api/test-cors` | Test CORS configuration with detailed response | JSON |
| `/api/debug-request` | Detailed request inspection with headers and environment | JSON |
| `/ultra-simple` | Ultra-minimal response with no dependencies | Text |
| `/feedback-tool-test` | Specialized endpoint for feedback tool testing | Text |
| `/diagnostic` | Interactive diagnostic page (template-based) | HTML |
| `/diagnostic-static` | Static diagnostic page (direct file serving) | HTML |

## Common Issues and Solutions

### CORS Misconfiguration

**Symptoms:**
- Web application feedback tool reports server is unreachable
- Browser console shows CORS errors
- Preflight OPTIONS requests fail

**Solutions:**
1. Ensure `FEEDBACK_TOOL_ORIGIN` environment variable is set correctly
2. Verify that CORS headers include the correct origin
3. Check that OPTIONS requests are properly handled
4. For credentials-based requests, ensure Access-Control-Allow-Credentials is 'true'

### Network Connectivity Issues

**Symptoms:**
- Timeout errors
- Connection refused errors
- Intermittent connectivity

**Solutions:**
1. Verify the server is running using the `/health` endpoint
2. Check if the server port (5000) is accessible
3. Ensure no firewall rules are blocking traffic
4. Test with cURL commands to isolate browser-specific issues

### API-Specific Issues

**Symptoms:**
- 404 errors on specific API endpoints
- Unexpected response formats
- Authentication failures

**Solutions:**
1. Use the `/api/debug-request` endpoint to inspect the exact request details
2. Verify API route definitions in `api_routes.py`
3. Check request and response formats using the Enhanced Diagnostic Tool

## Standalone Testing Server

For isolated testing, you can use the standalone minimal server:

```bash
python standalone_minimal_server.py
```

This runs a minimal Flask server with no dependencies, providing basic endpoints that can be used to verify connectivity from the feedback tool.

## Best Practices

1. **Use Explicit CORS Headers:** Always include explicit CORS headers rather than relying on the Flask-CORS extension defaults
2. **Test with Multiple Request Types:** Verify both GET and POST requests work correctly
3. **Monitor Server Logs:** Check server logs for detailed information about incoming requests
4. **Use the Enhanced Diagnostic Tool:** Make use of the comprehensive testing capabilities in the Enhanced Diagnostic Tool

## Additional Resources

For further assistance, refer to:
- [KNOWN_ISSUES.md](/static/markdown/KNOWN_ISSUES.md): Documentation of known issues and workarounds
- [README.md](/readme): Main project documentation
