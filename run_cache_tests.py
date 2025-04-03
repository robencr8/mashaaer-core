#!/usr/bin/env python3
"""
Script to run cache tests and display results in a structured format.
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime

def main():
    """Run cache tests and display results"""
    # Set up environment
    os.environ['TESTING'] = 'True'
    
    # Record start time
    start_time = time.time()
    
    # Print header
    print("=" * 80)
    print(f"CACHE TESTING SUITE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Run pytest for cache-related tests
    cmd = ["python", "-m", "pytest", "tests/test_api_caching.py", "-v"]
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 80)
    
    # Execute pytest
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Display output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("ERRORS:")
            print(result.stderr)
            
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Print summary
        print("=" * 80)
        print(f"Tests completed in {execution_time:.2f} seconds")
        print(f"Exit code: {result.returncode}")
        
        # Parse test results
        if "FAILED" in result.stdout:
            failed_count = result.stdout.count("FAILED")
            print(f"❌ {failed_count} tests failed")
        else:
            print("✅ All tests passed")
            
        # Save results to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"cache_test_results_{timestamp}.json"
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "execution_time_seconds": execution_time,
            "exit_code": result.returncode,
            "passed": result.returncode == 0,
            "raw_output": result.stdout
        }
        
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2)
            
        print(f"Results saved to {results_file}")
        print("=" * 80)
        
        # Return exit code from pytest
        return result.returncode
        
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())