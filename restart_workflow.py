"""
Script to restart the 'Start application' workflow and test its health.
"""
import requests
import time
import os
import subprocess

def run_command(command):
    """Run a shell command and return its output."""
    print(f"Running command: {command}")
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    return process.stdout

def check_health(url, max_retries=20, retry_delay=1):
    """Check if the server is healthy."""
    print(f"Checking health at: {url}")
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"Health check successful: {response.json()}")
                return True
            else:
                print(f"Attempt {i+1}/{max_retries}: Unexpected status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Attempt {i+1}/{max_retries}: Failed to connect: {e}")
        
        if i < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    print("Health check failed after all retries.")
    return False

def main():
    """Restart the workflow and check its health."""
    # Kill any existing processes on port 5000
    print("Checking for processes on port 5000...")
    run_command("lsof -i :5000 | grep LISTEN")
    
    # Find the .replit file and extract workflow configuration
    print("\nChecking .replit configuration...")
    replit_content = ""
    try:
        with open('.replit', 'r') as f:
            replit_content = f.read()
            print("Found .replit file.")
    except FileNotFoundError:
        print(".replit file not found.")
    
    # Restart the workflow
    print("\nRestarting the 'Start application' workflow...")
    workflow_started = False
    try:
        subprocess.run(["replit", "workflow", "restart", "Start application"], check=True)
        workflow_started = True
        print("Workflow restart command succeeded.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Failed to restart workflow: {e}")
    
    # Give the workflow time to start
    print("\nWaiting for workflow to start...")
    time.sleep(5)
    
    # Check if the server is responding
    if workflow_started:
        print("\nChecking if server is responding...")
        if check_health("http://localhost:5000/health"):
            print("\nServer is up and running!")
        else:
            print("\nServer failed to start properly.")
    
    print("\nWorkflow restart process completed.")

if __name__ == "__main__":
    main()