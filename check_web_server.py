"""
Script to check web server accessibility from different contexts.
"""
import os
import sys
import requests
import time
import json
import socket
import subprocess

def check_url(url, max_retries=3, retry_delay=1):
    """Check if a URL is accessible and return details."""
    print(f"Checking URL: {url}")
    results = {"url": url, "accessible": False, "status_code": None, "content_length": None, "error": None}
    
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            results["accessible"] = True
            results["status_code"] = response.status_code
            results["content_length"] = len(response.content)
            results["content_type"] = response.headers.get('Content-Type')
            results["content_preview"] = response.content[:100].decode('utf-8', errors='replace') if response.content else ""
            return results
        except requests.exceptions.RequestException as e:
            results["error"] = str(e)
            if i < max_retries - 1:
                time.sleep(retry_delay)
    
    return results

def check_port(host, port):
    """Check if a port is open on a host."""
    print(f"Checking if port {port} is open on {host}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    return {"host": host, "port": port, "open": result == 0}

def get_process_info(port):
    """Get information about processes listening on the specified port."""
    print(f"Getting process info for port {port}")
    try:
        output = subprocess.check_output(f"lsof -i :{port}", shell=True, text=True)
        return {"port": port, "process_info": output.strip()}
    except subprocess.CalledProcessError:
        return {"port": port, "process_info": "No process found listening on this port"}

def check_dns_resolution(domain):
    """Check DNS resolution for a domain."""
    print(f"Checking DNS resolution for {domain}")
    try:
        ip = socket.gethostbyname(domain)
        return {"domain": domain, "resolved": True, "ip": ip}
    except socket.gaierror:
        return {"domain": domain, "resolved": False, "error": "DNS resolution failed"}

def get_environment_info():
    """Get information about the environment."""
    print("Getting environment info")
    info = {
        "python_version": sys.version,
        "platform": sys.platform,
        "cwd": os.getcwd(),
        "env_vars": {k: v for k, v in os.environ.items() if k.startswith("REPL") or k in ["PORT", "HOST", "FLASK_ENV", "FLASK_DEBUG"]}
    }
    return info

def main():
    """Run all checks and print results."""
    results = {}
    
    # Check local URLs
    results["local_url_checks"] = [
        check_url("http://localhost:5000/"),
        check_url("http://127.0.0.1:5000/"),
        check_url("http://0.0.0.0:5000/"),
        check_url("http://localhost:5000/health"),
        check_url("http://localhost:5000/replit-test"),
        check_url("http://localhost:5000/static/replit_test.html")
    ]
    
    # Check ports
    results["port_checks"] = [
        check_port("localhost", 5000),
        check_port("127.0.0.1", 5000),
        check_port("0.0.0.0", 5000)
    ]
    
    # Get process info
    results["process_info"] = get_process_info(5000)
    
    # Check DNS resolution
    hostname = socket.gethostname()
    results["dns_checks"] = [
        check_dns_resolution("localhost"),
        check_dns_resolution(hostname)
    ]
    
    # Get environment info
    results["environment_info"] = get_environment_info()
    
    # Print results
    print("\n=== Web Server Accessibility Check Results ===")
    print(json.dumps(results, indent=2))
    
    # Summary
    print("\n=== Summary ===")
    accessible_urls = [result["url"] for result in results["local_url_checks"] if result["accessible"]]
    print(f"Accessible URLs: {len(accessible_urls)}/{len(results['local_url_checks'])}")
    if accessible_urls:
        print("URLs that are accessible:")
        for url in accessible_urls:
            print(f"  - {url}")
    
    open_ports = [result["port"] for result in results["port_checks"] if result["open"]]
    print(f"Open ports: {len(open_ports)}/{len(results['port_checks'])}")
    
    print("\nDetailed results have been printed above.")

if __name__ == "__main__":
    main()