import requests
import sys

url = "http://localhost:5000"
try:
    response = requests.get(url)
    print(f"Server Status: {'OK' if response.status_code == 200 else 'Error'}")
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.text)} bytes")
    print("First 200 characters of response:")
    print(response.text[:200])
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)