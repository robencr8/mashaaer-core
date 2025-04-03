#!/usr/bin/env python3
"""
Script to find dead (unused) code in the project.
This script uses the vulture library to identify potentially unused code.
"""

import os
import sys
import subprocess
from pathlib import Path


def ensure_vulture_installed():
    """Ensure vulture is installed."""
    try:
        import vulture
        print(f"Using vulture version {vulture.__version__}")
        return True
    except ImportError:
        print("Vulture not found, installing...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "vulture"],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing vulture: {e}")
            print(f"Error details: {e.stderr}")
            return False


def find_dead_code():
    """Find potentially unused code in the project."""
    print("Scanning for potentially unused code...")
    
    # Define directories and files to exclude
    exclude_dirs = [
        "venv",
        ".venv",
        "__pycache__",
        ".git",
        "android/.buildozer",
        "android/bin",
        "logs",
        "temp",
        "tts_cache"
    ]
    
    # Create a whitelist file to reduce false positives
    whitelist_content = """
    # Whitelist for vulture
    # Add patterns for known false positives here
    
    # Flask routes
    app.route
    render_template
    jsonify
    request.args
    request.form
    request.json
    
    # Database models
    Column
    ForeignKey
    relationship
    backref
    
    # Common special methods
    __init__
    __str__
    __repr__
    __enter__
    __exit__
    
    # Configuration and environment variables
    os.environ
    os.getenv
    config.get
    
    # Event handlers and callbacks
    on_press
    on_release
    on_touch_down
    on_touch_up
    on_touch_move
    """
    
    whitelist_path = Path("vulture_whitelist.txt")
    with open(whitelist_path, "w") as f:
        f.write(whitelist_content)
    
    # Build the command to run vulture
    cmd = [
        sys.executable, "-m", "vulture",
        ".", whitelist_path,
        "--exclude", ",".join(exclude_dirs),
        "--min-confidence", "80"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        # Check if any unused code was found
        if result.stdout.strip():
            print("\nPotentially unused code found:")
            print(result.stdout)
            
            # Save results to a file
            results_file = Path("dead_code_report.txt")
            with open(results_file, "w") as f:
                f.write("# Dead Code Report\n")
                f.write("# Generated on: " + subprocess.check_output(["date"]).decode().strip() + "\n\n")
                f.write("The following code appears to be unused (confidence >= 80%):\n\n")
                f.write(result.stdout)
                f.write("\n\nNote: This is an automated analysis and may include false positives.\n")
                f.write("Please review each case before removing code.\n")
            
            print(f"\nDetailed report saved to: {results_file}")
        else:
            print("No unused code found with confidence >= 80%")
        
        # Show errors if any
        if result.stderr:
            print("\nErrors encountered:")
            print(result.stderr)
        
        return True
    
    except Exception as e:
        print(f"Error running vulture: {e}")
        return False
    
    finally:
        # Clean up whitelist file
        if whitelist_path.exists():
            whitelist_path.unlink()


def main():
    """Main function."""
    print("Mashaaer Feelings - Dead Code Finder")
    print("=====================================")
    
    if ensure_vulture_installed():
        find_dead_code()
    else:
        print("Failed to run dead code analysis")


if __name__ == "__main__":
    main()