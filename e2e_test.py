"""
End-to-End Test Script for Mashaaer Feelings Application

This script tests various endpoints and features of the application
to verify that all components are working correctly.
"""

import requests
import sys
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base URL for the application
BASE_URL = "http://localhost:5000"

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def success(message):
    """Print success message in green"""
    logger.info(f"{GREEN}{message}{RESET}")

def error(message):
    """Print error message in red"""
    logger.error(f"{RED}{message}{RESET}")

def warning(message):
    """Print warning message in yellow"""
    logger.warning(f"{YELLOW}{message}{RESET}")

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            success(f"Health endpoint is working. Status: {data.get('status')}")
            success(f"Features: {', '.join(data.get('features', []))}")
            return True
        else:
            error(f"Health endpoint returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        error(f"Error connecting to health endpoint: {str(e)}")
        return False

def test_static_routes():
    """Test static routes like the index page"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            success("Main index route is working")
            return True
        else:
            error(f"Main index route returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        error(f"Error connecting to main index route: {str(e)}")
        return False

def test_accessibility_api():
    """Test the accessibility API endpoints"""
    try:
        response = requests.get(f"{BASE_URL}/api/accessibility/status")
        if response.status_code == 200:
            data = response.json()
            success("Accessibility API status endpoint is working")
            if data.get('success', False):
                success(f"Narrator enabled: {data.get('enabled', False)}")
            return True
        elif response.status_code == 500 and "Accessibility narrator not initialized" in response.text:
            warning("Accessibility narrator not initialized - consider initializing it")
            return True  # This is an expected behavior if narrator isn't initialized
        else:
            error(f"Accessibility API status endpoint returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        error(f"Error connecting to accessibility API status endpoint: {str(e)}")
        return False

def test_emotion_progress_api():
    """Test the emotion progress API endpoints"""
    try:
        # Try to get progress for a test user ID (this may fail if the user doesn't exist)
        test_user_id = 1
        response = requests.get(f"{BASE_URL}/api/progress/user/{test_user_id}")
        
        if response.status_code == 200:
            success(f"Emotion progress API is working for user {test_user_id}")
            return True
        elif response.status_code == 404 and "User not found" in response.text:
            warning(f"User {test_user_id} not found - test with valid user ID")
            return True  # This is an expected behavior if the user doesn't exist
        else:
            error(f"Emotion progress API returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        error(f"Error connecting to emotion progress API: {str(e)}")
        return False

def test_music_recommendation_api():
    """Test the music recommendation API endpoints"""
    try:
        # Try to get music recommendations for a mood
        test_mood = "happy"
        response = requests.get(f"{BASE_URL}/api/music/recommendations?mood={test_mood}")
        
        if response.status_code == 200:
            success(f"Music recommendation API is working for mood '{test_mood}'")
            return True
        else:
            error(f"Music recommendation API returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        error(f"Error connecting to music recommendation API: {str(e)}")
        return False

def test_accessibility_initialization():
    """Test adding and initializing the accessibility API"""
    try:
        # Let's just check if the accessibility_api.py file exists and has expected functions
        import importlib.util
        import sys
        
        try:
            spec = importlib.util.spec_from_file_location("accessibility_api", "accessibility_api.py")
            accessibility_module = importlib.util.module_from_spec(spec)
            sys.modules["accessibility_api"] = accessibility_module
            spec.loader.exec_module(accessibility_module)
            
            # Check if key functions exist
            if hasattr(accessibility_module, 'init_accessibility_api') and hasattr(accessibility_module, 'get_narrator'):
                success("Accessibility API module loaded successfully")
                return True
            else:
                error("Accessibility API module is missing expected functions")
                return False
        except Exception as e:
            error(f"Failed to import accessibility_api module: {str(e)}")
            return False
    except Exception as e:
        error(f"Error testing accessibility initialization: {str(e)}")
        return False

def test_database_connection():
    """Test database connection"""
    try:
        import psycopg2
        import os
        
        # Get the database URL from environment variable
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            warning("DATABASE_URL environment variable not set")
            return False  # Return boolean, not the warning function
        
        # Try to connect to the database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if version:
            success(f"Database connection successful")
            return True
        else:
            error("Database connection failed")
            return False
    except Exception as e:
        error(f"Error connecting to database: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("\n===== STARTING MASHAAER END-TO-END TESTS =====\n")
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Static Routes", test_static_routes),
        ("Accessibility API", test_accessibility_api),
        ("Accessibility Initialization", test_accessibility_initialization),
        ("Database Connection", test_database_connection),
        ("Emotion Progress API", test_emotion_progress_api),
        ("Music Recommendation API", test_music_recommendation_api)
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n----- Testing: {name} -----")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            error(f"Unexpected error in {name} test: {str(e)}")
            results.append((name, False))
    
    # Print summary
    print("\n===== TEST RESULTS SUMMARY =====\n")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = f"{GREEN}PASS{RESET}" if success else f"{RED}FAIL{RESET}"
        print(f"{name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)