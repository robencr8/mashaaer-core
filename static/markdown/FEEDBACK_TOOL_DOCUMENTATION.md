# Feedback Tool Integration Documentation

## Overview

This document provides technical documentation for integrating the web application feedback tool with the Mashaaer Feelings application. It covers API endpoints, CORS configuration, troubleshooting procedures, and known limitations.

## Health Check Endpoints

### 1. Root Level Health Check

```
GET /health
```

- **Purpose**: Ultra-minimal health check endpoint at root level
- **Response**: Plain text "OK"
- **Content-Type**: text/plain
- **CORS**: Fully enabled with all necessary headers
- **Example**: `curl -v http://localhost:5000/health`

### 2. API Status

```
GET /api/status
```

- **Purpose**: Get comprehensive system status information
- **Response**: JSON object with system status details
- **Content-Type**: application/json
- **CORS**: Fully enabled with all necessary headers
- **Example**: `curl -v http://localhost:5000/api/status`

### 3. API Ping

```
GET /api/ping
```

- **Purpose**: Simple ping endpoint for connectivity testing
- **Response**: JSON with success message
- **Content-Type**: application/json
- **CORS**: Fully enabled with all necessary headers
- **Example**: `curl -v http://localhost:5000/api/ping`

## Minimal Endpoints

### 1. Minimal API

```
GET /api/minimal
```

- **Purpose**: Minimal API endpoint returning plain text
- **Response**: Plain text message
- **Content-Type**: text/plain
- **CORS**: Fully enabled with all necessary headers
- **Example**: `curl -v http://localhost:5000/api/minimal`

### 2. Minimal Page

```
GET /minimal-page
```

- **Purpose**: Serve minimal HTML page with no dependencies
- **Response**: HTML document
- **Content-Type**: text/html
- **Example**: Open in browser: http://localhost:5000/minimal-page

### 3. Ultra Minimal Page

```
GET /ultra-minimal
```

- **Purpose**: Serve ultra-minimal HTML with zero dependencies
- **Response**: HTML document
- **Content-Type**: text/html
- **Example**: Open in browser: http://localhost:5000/ultra-minimal

## Dedicated Feedback Tool Endpoints

### 1. Feedback Tool Endpoint

```
POST /feedback-tool-endpoint
OPTIONS /feedback-tool-endpoint
```

- **Purpose**: Optimized endpoint for the feedback tool
- **Response**: JSON with success status
- **Content-Type**: application/json
- **CORS**: Fully enabled with explicit preflight support
- **Example**:
  ```
  curl -X POST -H "Content-Type: application/json" -H "Origin: http://example.com" \
    -d '{"test":"data"}' http://localhost:5000/feedback-tool-endpoint
  ```

### 2. Feedback Tool Status

```
GET /api/feedback-tool-status
```

- **Purpose**: Enhanced diagnostic endpoint with detailed information
- **Response**: JSON with detailed request and server information
- **Content-Type**: application/json
- **CORS**: Fully enabled with all necessary headers
- **Example**: `curl -v http://localhost:5000/api/feedback-tool-status`

## Diagnostic Tools

### 1. Debug Request

```
GET /api/debug-request
```

- **Purpose**: Detailed request information for debugging
- **Response**: JSON with comprehensive request details
- **Content-Type**: application/json
- **CORS**: Fully enabled with all necessary headers
- **Example**: `curl -v http://localhost:5000/api/debug-request`

### 2. CORS Diagnostic

```
GET /cors-diagnostic
```

- **Purpose**: Interactive CORS testing and debugging tool
- **Response**: HTML page with diagnostic tools
- **Content-Type**: text/html
- **Example**: Open in browser: http://localhost:5000/cors-diagnostic

### 3. Feedback Tool Diagnostic

```
GET /feedback-tool-diagnostic
```

- **Purpose**: Specialized diagnostic page for the feedback tool
- **Response**: HTML page with feedback tool diagnostics
- **Content-Type**: text/html
- **Example**: Open in browser: http://localhost:5000/feedback-tool-diagnostic

## CORS Configuration

All API endpoints are configured with the following CORS headers:

```
Access-Control-Allow-Origin: <dynamic based on request origin or '*'>
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: *
Access-Control-Max-Age: 3600
```

The application dynamically sets the `Access-Control-Allow-Origin` header based on the incoming request's `Origin` header, with fallback to `*` for maximum compatibility.

## Testing and Verification

### Curl Commands

```bash
# Test basic health check
curl -v http://localhost:5000/health

# Test with custom origin
curl -H "Origin: https://example.com" -v http://localhost:5000/api/status

# Test OPTIONS preflight
curl -X OPTIONS -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  -v http://localhost:5000/api/status

# Test feedback tool endpoint
curl -X POST -H "Content-Type: application/json" \
  -H "Origin: https://example.com" \
  -d '{"test":"data"}' http://localhost:5000/feedback-tool-endpoint
```

### Browser Testing

Open the following URLs in your browser:

- http://localhost:5000/cors-diagnostic
- http://localhost:5000/feedback-tool-diagnostic
- http://localhost:5000/feedback-comprehensive-test

## Known Issues and Troubleshooting

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for detailed information on known issues, workarounds, and troubleshooting procedures.
