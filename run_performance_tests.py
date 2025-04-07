#!/usr/bin/env python3
"""
End-to-End Performance Testing Script for Mashaaer
This script runs comprehensive performance tests on the Mashaaer application
and generates a detailed report of the results.
"""
import os
import sys
import time
import json
import argparse
import requests
import statistics
from datetime import datetime
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("performance_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("performance_tester")

# Default settings
DEFAULT_BASE_URL = "http://localhost:5000"
DEFAULT_CONCURRENT_REQUESTS = 10
DEFAULT_ITERATIONS = 3
DEFAULT_TIMEOUT = 30

class PerformanceTester:
    """
    Runs performance tests on the Mashaaer application and collects metrics.
    """
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: int = DEFAULT_TIMEOUT):
        """Initialize the performance tester with the given base URL"""
        self.base_url = base_url
        self.timeout = timeout
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "tests": {}
        }
        
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, 
                     headers: Dict = None, description: str = "") -> Dict[str, Any]:
        """
        Test a single endpoint and return timing metrics.
        
        Args:
            endpoint: The API endpoint to test (e.g., "/api-health")
            method: HTTP method to use (GET, POST, etc.)
            data: Optional data to send in the request body
            headers: Optional headers to include in the request
            description: Description of the test
            
        Returns:
            Dict with test results and timing metrics
        """
        if headers is None:
            headers = {"Content-Type": "application/json"}
            
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"Testing endpoint: {method} {url}")
        
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=self.timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            result = {
                "success": response.status_code >= 200 and response.status_code < 300,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
            
            # Try to parse the response as JSON
            try:
                result["response_data"] = response.json()
            except:
                # If not JSON, include the text (truncated if too long)
                text = response.text[:500] + ("..." if len(response.text) > 500 else "")
                result["response_text"] = text
                
            logger.info(f"Endpoint test complete: {method} {endpoint} - Status: {response.status_code}, Time: {response_time:.2f}ms")
            return result
            
        except requests.exceptions.Timeout:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            logger.error(f"Timeout error for endpoint: {method} {endpoint}")
            return {
                "success": False,
                "error": "Timeout",
                "response_time_ms": response_time,
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            logger.error(f"Request error for endpoint: {method} {endpoint}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": response_time,
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            logger.error(f"Unexpected error for endpoint: {method} {endpoint}: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "response_time_ms": response_time,
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
            
    def run_concurrent_test(self, endpoint: str, method: str = "GET", data: Dict = None,
                          headers: Dict = None, description: str = "", 
                          concurrent_requests: int = DEFAULT_CONCURRENT_REQUESTS) -> Dict[str, Any]:
        """
        Test an endpoint with concurrent requests.
        
        Args:
            endpoint: The API endpoint to test
            method: HTTP method to use
            data: Optional data to send in the request
            headers: Optional headers to include
            description: Description of the test
            concurrent_requests: Number of concurrent requests to make
            
        Returns:
            Dict with aggregated test results and timing metrics
        """
        logger.info(f"Running concurrent test on {endpoint} with {concurrent_requests} concurrent requests")
        
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [
                executor.submit(self.test_endpoint, endpoint, method, data, headers, description)
                for _ in range(concurrent_requests)
            ]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error in concurrent test: {str(e)}")
                    results.append({
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        
        # Calculate statistics
        successful_results = [r for r in results if r.get("success", False)]
        success_rate = len(successful_results) / len(results) if results else 0
        
        response_times = [r.get("response_time_ms", 0) for r in results if "response_time_ms" in r]
        
        stats = {
            "total_requests": len(results),
            "successful_requests": len(successful_results),
            "success_rate": success_rate,
            "total_time_ms": total_time,
            "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "median_response_time_ms": statistics.median(response_times) if response_times else 0,
            "requests_per_second": len(results) / (total_time / 1000) if total_time > 0 else 0,
        }
        
        if len(response_times) >= 2:
            stats["stdev_response_time_ms"] = statistics.stdev(response_times)
            
        logger.info(f"Concurrent test complete: {concurrent_requests} requests to {endpoint}")
        logger.info(f"Success rate: {success_rate:.2%}, Avg response time: {stats['avg_response_time_ms']:.2f}ms")
        
        return {
            "stats": stats,
            "individual_results": results
        }
    
    def run_test_suite(self, iterations: int = DEFAULT_ITERATIONS, 
                      concurrent_requests: int = DEFAULT_CONCURRENT_REQUESTS) -> Dict[str, Any]:
        """
        Run a full test suite of all API endpoints.
        
        Args:
            iterations: Number of test iterations to run
            concurrent_requests: Number of concurrent requests for load testing
            
        Returns:
            Dict with all test results
        """
        logger.info(f"Starting full test suite with {iterations} iterations")
        
        # Basic health check endpoints
        self.results["tests"]["api_health"] = self.test_endpoint(
            "/api-health",
            description="API Health Check"
        )
        
        self.results["tests"]["api_status"] = self.test_endpoint(
            "/api-status",
            description="API Status Check"
        )
        
        # Emotion detection - English
        self.results["tests"]["emotion_detection_en"] = self.test_endpoint(
            "/api/emotion",
            method="POST",
            data={"text": "I am feeling very happy today"},
            description="Emotion Detection - English"
        )
        
        # Emotion detection - Arabic
        self.results["tests"]["emotion_detection_ar"] = self.test_endpoint(
            "/api/emotion",
            method="POST",
            data={"text": "أنا سعيد جدا اليوم"},
            description="Emotion Detection - Arabic"
        )
        
        # Emotion detection - Mixed emotions
        self.results["tests"]["emotion_detection_mixed"] = self.test_endpoint(
            "/api/emotion",
            method="POST",
            data={"text": "I'm happy but also slightly worried"},
            description="Emotion Detection - Mixed Emotions"
        )
        
        # Voice logic - English
        self.results["tests"]["voice_logic_en"] = self.test_endpoint(
            "/api/voice_logic",
            method="POST",
            data={"text": "Welcome to Mashaaer", "language": "en"},
            description="Voice Logic - English"
        )
        
        # Voice logic - Arabic
        self.results["tests"]["voice_logic_ar"] = self.test_endpoint(
            "/api/voice_logic",
            method="POST",
            data={"text": "مرحبا بكم في مشاعر", "language": "ar"},
            description="Voice Logic - Arabic"
        )
        
        # Feedback verification
        self.results["tests"]["verify_feedback"] = self.test_endpoint(
            "/api/verify-feedback",
            description="Feedback Verification"
        )
        
        # User feedback submission
        self.results["tests"]["user_feedback"] = self.test_endpoint(
            "/api/user-feedback",
            method="POST",
            data={
                "name": "Test User",
                "feedback": "This is a test feedback for performance testing",
                "rating": 5,
                "emotion": "happy"
            },
            description="User Feedback Submission"
        )
        
        # Enhanced feedback submission
        self.results["tests"]["enhanced_feedback"] = self.test_endpoint(
            "/api/enhanced-feedback",
            method="POST",
            data={
                "name": "Test User",
                "feedback": "This is a test enhanced feedback for performance testing",
                "rating": 4,
                "emotion": "excited"
            },
            description="Enhanced Feedback Submission"
        )
        
        # Telegram notification
        self.results["tests"]["telegram_notification"] = self.test_endpoint(
            "/api/notifications/telegram/notify",
            method="POST",
            data={"message": "Test notification from performance testing"},
            description="Telegram Notification"
        )
        
        # System notification
        self.results["tests"]["system_notification"] = self.test_endpoint(
            "/api/notifications/telegram/system",
            method="POST",
            data={
                "type": "stats",
                "data": {
                    "users": 123,
                    "interactions": 456,
                    "api_calls": 789
                }
            },
            description="System Notification"
        )
        
        # Run concurrent load tests only on safe endpoints
        if iterations > 0:
            logger.info(f"Running load tests with {concurrent_requests} concurrent requests")
            
            self.results["load_tests"] = {}
            
            # Health check load test
            self.results["load_tests"]["api_health"] = self.run_concurrent_test(
                "/api-health",
                concurrent_requests=concurrent_requests,
                description="API Health Load Test"
            )
            
            # Status check load test
            self.results["load_tests"]["api_status"] = self.run_concurrent_test(
                "/api-status",
                concurrent_requests=concurrent_requests,
                description="API Status Load Test"
            )
            
            # Feedback verification load test
            self.results["load_tests"]["verify_feedback"] = self.run_concurrent_test(
                "/api/verify-feedback",
                concurrent_requests=concurrent_requests,
                description="Feedback Verification Load Test"
            )
            
        # Add test metadata
        self.results["metadata"] = {
            "test_completed": datetime.now().isoformat(),
            "iterations": iterations,
            "concurrent_requests": concurrent_requests,
            "base_url": self.base_url
        }
        
        logger.info("Test suite completed successfully")
        return self.results
    
    def save_results(self, filename: str = None) -> str:
        """
        Save test results to a JSON file.
        
        Args:
            filename: Optional filename to save results to
            
        Returns:
            Path to the saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_test_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
            
        logger.info(f"Test results saved to {filename}")
        return filename

    def print_summary(self) -> None:
        """Print a summary of the test results"""
        print("\n=== Mashaaer Performance Test Summary ===\n")
        print(f"Base URL: {self.results['base_url']}")
        print(f"Test completed: {self.results['metadata']['test_completed']}")
        print(f"Concurrent requests: {self.results['metadata']['concurrent_requests']}")
        print("\n--- API Endpoints ---")
        
        for name, result in self.results["tests"].items():
            status = "✅ SUCCESS" if result.get("success", False) else "❌ FAILED"
            time = f"{result.get('response_time_ms', 0):.2f}ms"
            print(f"{name}: {status} - {time}")
        
        if "load_tests" in self.results:
            print("\n--- Load Tests ---")
            for name, result in self.results["load_tests"].items():
                stats = result["stats"]
                success_rate = f"{stats['success_rate']:.2%}"
                avg_time = f"{stats['avg_response_time_ms']:.2f}ms"
                rps = f"{stats['requests_per_second']:.2f} req/s"
                print(f"{name}: Success rate: {success_rate}, Avg time: {avg_time}, Throughput: {rps}")
        
        print("\n========================================\n")

def main():
    """Main function to run the script from the command line"""
    parser = argparse.ArgumentParser(description="Mashaaer Performance Testing Script")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL of the Mashaaer API")
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS, help="Number of test iterations")
    parser.add_argument("--concurrent", type=int, default=DEFAULT_CONCURRENT_REQUESTS, help="Number of concurrent requests")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Request timeout in seconds")
    parser.add_argument("--output", help="Output file path for test results")
    
    args = parser.parse_args()
    
    tester = PerformanceTester(base_url=args.base_url, timeout=args.timeout)
    tester.run_test_suite(iterations=args.iterations, concurrent_requests=args.concurrent)
    
    if args.output:
        tester.save_results(args.output)
    else:
        tester.save_results()
    
    tester.print_summary()
    
if __name__ == "__main__":
    main()