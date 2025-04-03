# Ngrok Setup for External API Access

## Overview

This guide explains how to use Ngrok with the مشاعر | Mashaaer application to enable external devices to access the API server.

## What is Ngrok?

Ngrok is a tool that creates secure tunnels to expose local web servers to the internet. It allows external devices and services to access your locally running server without having to set up complex networking configurations.

## Why Use Ngrok with مشاعر | Mashaaer?

The مشاعر | Mashaaer application runs a web server locally on port 5000. This works fine for local testing, but if you want to:

1. Access the API from a mobile device
2. Test with external tools like the web application feedback tool
3. Demonstrate the application to others
4. Avoid CORS issues

Then you need to make your local server accessible from the internet, which is where Ngrok comes in.

## Setup Instructions

### 1. Install Ngrok

If you haven't already, you can install Ngrok by:
- Visiting [ngrok.com](https://ngrok.com/)
- Signing up for a free account
- Following their installation instructions

### 2. Start Ngrok Tunnel

With Ngrok installed, open a new terminal and run:

```bash
ngrok http 5000
```

This will create a tunnel to your local server on port 5000 and display a URL like:

```
Forwarding https://abc123def456.ngrok-free.app -> http://localhost:5000
```

### 3. Configure مشاعر | Mashaaer to Use Ngrok URL

1. Open the diagnostic page at: http://localhost:5000/
2. In the "External URL Configuration" section, enter your Ngrok URL (e.g., https://abc123def456.ngrok-free.app)
3. Click "Update URL"
4. Test the connection by clicking the "Test API Status" button

### 4. Access from External Devices

Once configured, you can:
- Access the application from mobile devices using the Ngrok URL
- Use external testing tools like the web application feedback tool
- Share the URL with others for demo purposes

## Troubleshooting

### CORS Issues

If you're experiencing CORS issues when accessing from external devices:

1. Make sure you're using the Ngrok URL in your API requests
2. Verify that the CORS headers are properly set (test using the "Test CORS" button on the diagnostic page)
3. Check the browser console for specific CORS errors

### Connection Refused

If you get "Connection Refused" errors:

1. Ensure your مشاعر | Mashaaer server is running on port 5000
2. Check that Ngrok is running and connected
3. Verify the Ngrok URL is correct and up-to-date

### Session Management

Note that session cookies might not work across different domains. If you're experiencing session-related issues:

1. Clear cookies in your browser
2. Restart your session from the beginning
3. Consider implementing token-based authentication for cross-domain access

## Limitations

- Free Ngrok accounts have limitations on connection time and bandwidth
- Ngrok URLs expire when you restart Ngrok
- Some advanced features may require a paid Ngrok subscription