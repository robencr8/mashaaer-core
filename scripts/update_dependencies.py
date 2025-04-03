#!/usr/bin/env python3
"""
Script to update and manage project dependencies.
This script will:
1. Update the requirements.txt file
2. Ensure consistency between requirements.txt and pyproject.toml
3. Check for outdated dependencies
4. Check for vulnerabilities in dependencies
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def create_dir_if_not_exists(path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def run_command(command, capture_output=True):
    """Run a shell command and return the output."""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=True,
            check=True
        )
        return result.stdout if capture_output else "Command executed successfully"
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"Command output: {e.output}")
        print(f"Command error: {e.stderr}")
        return None


def update_requirements_txt():
    """Update requirements.txt from pyproject.toml."""
    print("Updating requirements.txt from pyproject.toml...")
    
    # Check if pyproject.toml exists
    if not os.path.exists("pyproject.toml"):
        print("Error: pyproject.toml not found")
        return False
    
    try:
        # Install toml package if not available
        try:
            import toml
        except ImportError:
            run_command([sys.executable, "-m", "pip", "install", "toml"])
            import toml
        
        # Parse pyproject.toml
        with open("pyproject.toml", "r") as f:
            pyproject = toml.load(f)
        
        # Extract dependencies
        dependencies = pyproject.get("project", {}).get("dependencies", [])
        if not dependencies:
            print("No dependencies found in pyproject.toml")
            return False
        
        # Create requirements.txt
        with open("requirements.txt", "w") as f:
            for dep in dependencies:
                # Remove any version specifier for cleaner output
                package_name = dep.split(">=")[0].split("==")[0].split("<")[0].strip()
                version_spec = dep[len(package_name):].strip()
                f.write(f"{package_name}{version_spec}\n")
        
        print("requirements.txt updated successfully")
        return True
    
    except Exception as e:
        print(f"Error updating requirements.txt: {e}")
        return False


def check_outdated_packages():
    """Check for outdated packages."""
    print("\nChecking for outdated packages...")
    
    # Run pip list --outdated in JSON format
    output = run_command([
        sys.executable, "-m", "pip", "list", "--outdated", "--format=json"
    ])
    
    if output:
        try:
            outdated = json.loads(output)
            if outdated:
                print("The following packages are outdated:")
                for package in outdated:
                    print(f"  {package['name']}: {package['version']} -> {package['latest_version']}")
            else:
                print("All packages are up to date")
        except json.JSONDecodeError:
            print("Error parsing pip output")
    else:
        print("Failed to check for outdated packages")


def check_vulnerabilities():
    """Check for vulnerabilities in dependencies."""
    print("\nChecking for security vulnerabilities...")
    
    # Check if safety is installed
    safety_installed = run_command([
        sys.executable, "-m", "pip", "show", "safety"
    ])
    
    if not safety_installed:
        print("Installing safety for vulnerability checking...")
        run_command([sys.executable, "-m", "pip", "install", "safety"])
    
    # Run safety check
    safety_output = run_command([
        sys.executable, "-m", "safety", "check", "--full-report"
    ], capture_output=True)
    
    if safety_output:
        if "No known security vulnerabilities found" in safety_output:
            print("No known security vulnerabilities found")
        else:
            print("Security vulnerabilities found:")
            print(safety_output)
    else:
        print("Failed to check for vulnerabilities")


def update_dev_dependencies():
    """Update development dependencies."""
    print("\nUpdating development dependencies...")
    
    dev_dependencies = [
        "black",
        "flake8",
        "isort",
        "pytest",
        "pytest-cov",
        "vulture",
        "safety"
    ]
    
    run_command([
        sys.executable, "-m", "pip", "install", "--upgrade"
    ] + dev_dependencies)
    
    print("Development dependencies updated")


def main():
    """Main function."""
    # Ensure script directory exists
    create_dir_if_not_exists("scripts")
    
    print("Mashaaer Feelings - Dependency Manager")
    print("======================================")
    
    # Update requirements.txt
    update_requirements_txt()
    
    # Check for outdated packages
    check_outdated_packages()
    
    # Check for vulnerabilities
    check_vulnerabilities()
    
    # Update development dependencies
    update_dev_dependencies()
    
    print("\nDependency management completed")


if __name__ == "__main__":
    main()