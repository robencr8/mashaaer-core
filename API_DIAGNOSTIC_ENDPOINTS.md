# API and Diagnostic Endpoints Reference

This document provides a comprehensive list of endpoints available for testing and diagnostics in the Mashaaer application.

## Simple Test Endpoints

| Endpoint | Method | Description | Response Type |
|----------|--------|-------------|--------------|
| `/test` | GET | Basic test endpoint | JSON |
| `/ultra-simple` | GET | Minimal endpoint with text response | Plain Text |
| `/feedback-tool-test` | GET | Ultra-minimal test for feedback tool | Plain Text |

## API Endpoints

| Endpoint | Method | Description | Response Type |
|----------|--------|-------------|--------------|
| `/api/ping` | GET | Simple API connectivity test | JSON |
| `/api/status` | GET | Detailed system status information | JSON |
| `/api/minimal` | GET | Minimal API with plain text response | Plain Text |
| `/api/test-cors` | GET, POST | CORS testing endpoint | JSON |
| `/api/test-cors-minimal` | GET, POST | Ultra-minimal CORS test | JSON |
| `/api/debug-request` | GET, POST | Detailed request debugging | JSON |

## Diagnostic Pages

| Endpoint | Description |
|----------|-------------|
| `/connection-test` | Basic connectivity test page |
| `/cors-test` | CORS testing page |
| `/cors-test-enhanced` | Enhanced CORS test with advanced features |
| `/cors-test-advanced` | Advanced CORS test with detailed diagnostics |
| `/diagnostic` | Comprehensive diagnostic page |
| `/diagnostic-tool` | Interactive diagnostic tool with auto-tests |
| `/feedback-tool-diagnostic` | Specialized diagnostic for feedback tool |
| `/diagnostic-panel` | Developer diagnostic panel |

## Testing Procedure

For manual testing:
1. Access the diagnostic endpoints directly in a browser
2. Use the diagnostic pages to run interactive tests
3. Use curl for testing API endpoints from command line

Example curl commands:
```bash
# Test basic connectivity
curl -v http://localhost:5000/test

# Test minimal endpoint
curl -v http://localhost:5000/ultra-simple

# Test API ping
curl -v http://localhost:5000/api/ping

# Test API status
curl -v http://localhost:5000/api/status
```

## CORS Headers

All API endpoints include these CORS headers for maximum compatibility:
- `Access-Control-Allow-Origin: *` (or echo back Origin header)
- `Access-Control-Allow-Methods: GET, POST, OPTIONS` (method-specific)
- `Access-Control-Allow-Headers: *` (or Content-Type, Authorization, X-Requested-With)
