"""
Test script to verify various ways to run the Mashaaer Feelings application.
"""
import os
import sys
import requests
import time
import subprocess
import signal

def test_endpoint(url, max_retries=5, retry_delay=2):
    """Test if an endpoint is responding."""
    print(f"Testing endpoint: {url}")
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            print(f"  Response status: {response.status_code}")
            print(f"  Response content: {response.text[:100]}...")
            return True
        except requests.RequestException as e:
            print(f"  Attempt {i+1}/{max_retries} failed: {e}")
            if i < max_retries - 1:
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    return False

def run_command(command, timeout=10):
    """Run a command and return its process."""
    print(f"Running command: {command}")
    process = subprocess.Popen(command, shell=True)
    print(f"  Process started with PID: {process.pid}")
    time.sleep(timeout)  # Wait for the process to start
    return process

def kill_process(process):
    """Kill a process."""
    if process:
        print(f"Killing process with PID: {process.pid}")
        try:
            os.kill(process.pid, signal.SIGTERM)
            process.wait(timeout=5)
        except (subprocess.TimeoutExpired, ProcessLookupError) as e:
            print(f"  Error killing process: {e}")
            try:
                os.kill(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

def main():
    """Run tests for different ways to start the server."""
    processes = []
    
    # Test 1: Direct Python execution
    print("\n=== Test 1: Direct Python execution ===")
    process = run_command("python main.py")
    processes.append(process)
    success = test_endpoint("http://localhost:5000/health")
    print(f"  Direct Python execution test {'succeeded' if success else 'failed'}")
    kill_process(process)
    
    # Test 2: Gunicorn execution
    print("\n=== Test 2: Gunicorn execution ===")
    process = run_command("gunicorn --bind 0.0.0.0:5000 --reuse-port main:app")
    processes.append(process)
    success = test_endpoint("http://localhost:5000/health")
    print(f"  Gunicorn execution test {'succeeded' if success else 'failed'}")
    kill_process(process)
    
    # Test 3: Python RobinAI_Enhanced execution
    print("\n=== Test 3: Python RobinAI_Enhanced execution ===")
    process = run_command("python RobinAI_Enhanced/main.py")
    processes.append(process)
    success = test_endpoint("http://localhost:5000/health")
    print(f"  Python RobinAI_Enhanced execution test {'succeeded' if success else 'failed'}")
    kill_process(process)
    
    # Test 4: Minimal app execution
    print("\n=== Test 4: Minimal app execution ===")
    process = run_command("python minimal_app.py")
    processes.append(process)
    success = test_endpoint("http://localhost:5000/health")
    print(f"  Minimal app execution test {'succeeded' if success else 'failed'}")
    kill_process(process)
    
    print("\n=== Summary ===")
    print("All tests completed. Check the output above for results.")
    
    # Clean up any remaining processes
    for p in processes:
        kill_process(p)

if __name__ == "__main__":
    main()