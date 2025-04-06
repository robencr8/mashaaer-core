"""
Comprehensive Test Script for Mashaaer PWA

This script tests all major functionalities of the Mashaaer Feelings application
by directly interacting with the backend APIs and verifying responses.
"""

import json
import os
import time
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_results.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MashaaerTester:
    """Comprehensive tester for Mashaaer application"""
    
    def __init__(self, base_url="http://localhost:5000"):
        """Initialize with the base URL of the application"""
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": base_url,
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }
    
    def run_all_tests(self):
        """Run all test methods in this class"""
        logger.info(f"Starting comprehensive tests against {self.base_url}")
        
        # Backend API tests
        self.test_server_health()
        self.test_emotion_analysis_api()
        self.test_chat_api()
        self.test_contextual_recommendations()
        self.test_idiom_translation()
        self.test_cosmic_sound()
        
        # Advanced system tests
        self.test_voice_processing()
        self.test_bilingual_support()
        self.test_cache_system()
        
        # Save results
        self.save_results()
        self.print_summary()
        
        return self.test_results
    
    def record_result(self, test_name, status, details=None):
        """Record a test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details or {}
        }
        self.test_results["tests"].append(result)
        self.test_results["summary"]["total"] += 1
        if status == "PASS":
            self.test_results["summary"]["passed"] += 1
            logger.info(f"TEST PASSED: {test_name}")
        else:
            self.test_results["summary"]["failed"] += 1
            logger.error(f"TEST FAILED: {test_name} - {details}")
    
    def test_server_health(self):
        """Test if the server is up and responding"""
        try:
            response = self.session.get(f"{self.base_url}/direct-feedback")
            if response.status_code == 200:
                self.record_result("Server Health", "PASS", {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                })
            else:
                self.record_result("Server Health", "FAIL", {
                    "status_code": response.status_code,
                    "response": response.text
                })
        except Exception as e:
            self.record_result("Server Health", "FAIL", {"error": str(e)})
    
    def test_emotion_analysis_api(self):
        """Test the emotion analysis API"""
        try:
            # Test happy emotion
            happy_text = "I am feeling really great today!"
            response = self.session.post(
                f"{self.base_url}/api/analyze-emotion",
                json={"text": happy_text}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("primary_emotion") == "happy":
                    self.record_result("Emotion Analysis (Happy)", "PASS", {
                        "text": happy_text,
                        "detected_emotion": data.get("primary_emotion")
                    })
                else:
                    self.record_result("Emotion Analysis (Happy)", "FAIL", {
                        "text": happy_text,
                        "response": data
                    })
            else:
                self.record_result("Emotion Analysis (Happy)", "FAIL", {
                    "status_code": response.status_code
                })
                
            # Test sad emotion
            sad_text = "I feel so alone and depressed today."
            response = self.session.post(
                f"{self.base_url}/api/analyze-emotion",
                json={"text": sad_text}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("primary_emotion") == "sad":
                    self.record_result("Emotion Analysis (Sad)", "PASS", {
                        "text": sad_text,
                        "detected_emotion": data.get("primary_emotion")
                    })
                else:
                    self.record_result("Emotion Analysis (Sad)", "FAIL", {
                        "text": sad_text,
                        "response": data
                    })
            else:
                self.record_result("Emotion Analysis (Sad)", "FAIL", {
                    "status_code": response.status_code
                })
        except Exception as e:
            self.record_result("Emotion Analysis API", "FAIL", {"error": str(e)})
    
    def test_chat_api(self):
        """Test the chat API with different emotions"""
        try:
            # Test chat with happy emotion
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": "I just got promoted at work!",
                    "emotion": "happy",
                    "user_id": "test_user",
                    "lang": "en"
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("response"):
                    self.record_result("Chat API (Happy)", "PASS", {
                        "action": data.get("action"),
                        "rule_matched": data.get("rule_matched")
                    })
                else:
                    self.record_result("Chat API (Happy)", "FAIL", {
                        "response": data
                    })
            else:
                self.record_result("Chat API (Happy)", "FAIL", {
                    "status_code": response.status_code
                })
                
            # Test chat with sad emotion
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": "I feel alone today",
                    "emotion": "sad",
                    "user_id": "test_user",
                    "lang": "en"
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("action") == "offer_companionship":
                    self.record_result("Chat API (Sad)", "PASS", {
                        "action": data.get("action"),
                        "rule_matched": data.get("rule_matched")
                    })
                else:
                    self.record_result("Chat API (Sad)", "FAIL", {
                        "response": data
                    })
            else:
                self.record_result("Chat API (Sad)", "FAIL", {
                    "status_code": response.status_code
                })
        except Exception as e:
            self.record_result("Chat API", "FAIL", {"error": str(e)})
    
    def test_contextual_recommendations(self):
        """Test the contextual recommendations API"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/recommendations/contextual",
                json={
                    "emotion": "sad",
                    "user_id": "test_user",
                    "lang": "en",
                    "context": {
                        "time_of_day": "evening",
                        "day_of_week": "monday",
                        "season": "winter"
                    }
                }
            )
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    data.get("recommendation_id") and 
                    data.get("recommendations")):
                    
                    recommendation_sections = [
                        "immediate_actions",
                        "wellbeing_practices",
                        "social_connections",
                        "reflective_insights",
                        "contextual_suggestions"
                    ]
                    
                    missing_sections = [s for s in recommendation_sections 
                                       if s not in data.get("recommendations", {})]
                    
                    if not missing_sections:
                        self.record_result("Contextual Recommendations", "PASS", {
                            "recommendation_id": data.get("recommendation_id"),
                            "is_fallback": data.get("is_fallback", False)
                        })
                    else:
                        self.record_result("Contextual Recommendations", "FAIL", {
                            "missing_sections": missing_sections,
                            "response": data
                        })
                else:
                    self.record_result("Contextual Recommendations", "FAIL", {
                        "response": data
                    })
            else:
                self.record_result("Contextual Recommendations", "FAIL", {
                    "status_code": response.status_code
                })
        except Exception as e:
            self.record_result("Contextual Recommendations", "FAIL", {"error": str(e)})
    
    def test_idiom_translation(self):
        """Test the idiom translation API"""
        try:
            # English to Arabic
            response = self.session.post(
                f"{self.base_url}/api/translate-idiom",
                json={
                    "text": "break a leg",
                    "source_lang": "en",
                    "target_lang": "ar"
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("translation"):
                    self.record_result("Idiom Translation (EN->AR)", "PASS", {
                        "original": "break a leg",
                        "translation": data.get("translation")
                    })
                else:
                    self.record_result("Idiom Translation (EN->AR)", "FAIL", {
                        "response": data
                    })
            else:
                self.record_result("Idiom Translation (EN->AR)", "FAIL", {
                    "status_code": response.status_code
                })
                
            # Arabic to English
            response = self.session.post(
                f"{self.base_url}/api/translate-idiom",
                json={
                    "text": "على قلبي مثل العسل",
                    "source_lang": "ar",
                    "target_lang": "en"
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("translation"):
                    self.record_result("Idiom Translation (AR->EN)", "PASS", {
                        "original": "على قلبي مثل العسل",
                        "translation": data.get("translation")
                    })
                else:
                    self.record_result("Idiom Translation (AR->EN)", "FAIL", {
                        "response": data
                    })
            else:
                self.record_result("Idiom Translation (AR->EN)", "FAIL", {
                    "status_code": response.status_code
                })
        except Exception as e:
            self.record_result("Idiom Translation", "FAIL", {"error": str(e)})
    
    def test_cosmic_sound(self):
        """Test the cosmic sound API"""
        try:
            # Get sound info
            response = self.session.post(
                f"{self.base_url}/api/cosmic-sound",
                json={
                    "emotion": "happy",
                    "action": "info"
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("cosmic_soundscape"):
                    self.record_result("Cosmic Sound Info", "PASS", {
                        "emotion": "happy",
                        "track": data.get("cosmic_soundscape", {}).get("track")
                    })
                else:
                    self.record_result("Cosmic Sound Info", "FAIL", {
                        "response": data
                    })
            else:
                self.record_result("Cosmic Sound Info", "FAIL", {
                    "status_code": response.status_code
                })
                
            # Test direct sound file endpoint
            response = self.session.get(f"{self.base_url}/api/play-cosmic-sound/happy")
            if response.status_code == 200 and response.headers.get("Content-Type", "").startswith("audio/"):
                content_length = int(response.headers.get("Content-Length", 0))
                self.record_result("Cosmic Sound File", "PASS", {
                    "content_type": response.headers.get("Content-Type"),
                    "content_length": content_length
                })
            else:
                self.record_result("Cosmic Sound File", "FAIL", {
                    "status_code": response.status_code,
                    "content_type": response.headers.get("Content-Type")
                })
        except Exception as e:
            self.record_result("Cosmic Sound", "FAIL", {"error": str(e)})
    
    def test_voice_processing(self):
        """Test voice processing functionality"""
        # This is a simplified simulation since we can't send actual audio files easily
        try:
            # Check if TTS endpoint is working
            response = self.session.post(
                f"{self.base_url}/api/tts",
                json={
                    "text": "This is a test of the text to speech system.",
                    "language": "en"
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("audio_url"):
                    self.record_result("Text to Speech", "PASS", {
                        "audio_url": data.get("audio_url")
                    })
                    
                    # Verify the audio file is accessible
                    audio_url = data.get("audio_url")
                    if audio_url.startswith("/"):
                        audio_url = f"{self.base_url}{audio_url}"
                        
                    audio_response = self.session.get(audio_url)
                    if audio_response.status_code == 200:
                        self.record_result("TTS Audio File Access", "PASS", {
                            "content_type": audio_response.headers.get("Content-Type"),
                            "content_length": audio_response.headers.get("Content-Length")
                        })
                    else:
                        self.record_result("TTS Audio File Access", "FAIL", {
                            "status_code": audio_response.status_code
                        })
                else:
                    self.record_result("Text to Speech", "FAIL", {
                        "response": data
                    })
            else:
                self.record_result("Text to Speech", "FAIL", {
                    "status_code": response.status_code
                })
        except Exception as e:
            self.record_result("Voice Processing", "FAIL", {"error": str(e)})
    
    def test_bilingual_support(self):
        """Test bilingual support for Arabic and English"""
        try:
            # Test English
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": "Hello, how are you?",
                    "emotion": "neutral",
                    "user_id": "test_user",
                    "lang": "en"
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("response"):
                    self.record_result("Bilingual Support (English)", "PASS", {
                        "response": data.get("response")[:50] + "..." if len(data.get("response", "")) > 50 else data.get("response")
                    })
                else:
                    self.record_result("Bilingual Support (English)", "FAIL", {
                        "response": data
                    })
            else:
                self.record_result("Bilingual Support (English)", "FAIL", {
                    "status_code": response.status_code
                })
                
            # Test Arabic
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": "مرحبا، كيف حالك؟",
                    "emotion": "neutral",
                    "user_id": "test_user",
                    "lang": "ar"
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("response"):
                    self.record_result("Bilingual Support (Arabic)", "PASS", {
                        "response": data.get("response")[:50] + "..." if len(data.get("response", "")) > 50 else data.get("response")
                    })
                else:
                    self.record_result("Bilingual Support (Arabic)", "FAIL", {
                        "response": data
                    })
            else:
                self.record_result("Bilingual Support (Arabic)", "FAIL", {
                    "status_code": response.status_code
                })
        except Exception as e:
            self.record_result("Bilingual Support", "FAIL", {"error": str(e)})
    
    def test_cache_system(self):
        """Test the caching system"""
        try:
            # First call should be a cache miss
            start_time = time.time()
            response1 = self.session.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": "This is a unique test message for cache testing",
                    "emotion": "neutral",
                    "user_id": "test_user",
                    "lang": "en"
                }
            )
            time1 = time.time() - start_time
            
            if response1.status_code != 200:
                self.record_result("Cache System", "FAIL", {
                    "status_code": response1.status_code
                })
                return
                
            # Second call with same parameters should be a cache hit (faster)
            start_time = time.time()
            response2 = self.session.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": "This is a unique test message for cache testing",
                    "emotion": "neutral",
                    "user_id": "test_user",
                    "lang": "en"
                }
            )
            time2 = time.time() - start_time
            
            if response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                
                # Check if responses are identical
                responses_match = (data1.get("response") == data2.get("response"))
                
                # Check if second call was faster
                cache_speedup = time2 < time1
                
                if responses_match and cache_speedup:
                    self.record_result("Cache System", "PASS", {
                        "first_call_time": time1,
                        "second_call_time": time2,
                        "speedup": f"{(time1/time2 if time2 > 0 else 0):.2f}x"
                    })
                else:
                    self.record_result("Cache System", "FAIL", {
                        "responses_match": responses_match,
                        "cache_speedup": cache_speedup,
                        "first_call_time": time1,
                        "second_call_time": time2
                    })
            else:
                self.record_result("Cache System", "FAIL", {
                    "status_code": response2.status_code
                })
        except Exception as e:
            self.record_result("Cache System", "FAIL", {"error": str(e)})
    
    def save_results(self):
        """Save test results to a JSON file"""
        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(self.test_results, f, indent=2)
        logger.info(f"Test results saved to {filename}")
        return filename
    
    def print_summary(self):
        """Print a summary of test results"""
        summary = self.test_results["summary"]
        logger.info("=" * 50)
        logger.info(f"TEST SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Total tests: {summary['total']}")
        logger.info(f"Passed: {summary['passed']} ({summary['passed']/summary['total']*100:.1f}%)")
        logger.info(f"Failed: {summary['failed']} ({summary['failed']/summary['total']*100:.1f}%)")
        logger.info("=" * 50)
        
        # Print individual test results
        for test in self.test_results["tests"]:
            status_symbol = "✓" if test["status"] == "PASS" else "✗"
            logger.info(f"{status_symbol} {test['test']}")
        
        logger.info("=" * 50)


def test_multiple_environments():
    """Run tests against multiple environments"""
    environments = [
        {
            "name": "Local",
            "url": "http://localhost:5000"
        },
        {
            "name": "Replit",
            "url": "https://Mashaaer.repl.co"
        }
    ]
    
    results = {}
    
    for env in environments:
        logger.info(f"\nTesting environment: {env['name']} ({env['url']})")
        try:
            tester = MashaaerTester(env["url"])
            env_results = tester.run_all_tests()
            results[env["name"]] = env_results
        except Exception as e:
            logger.error(f"Failed to test environment {env['name']}: {str(e)}")
            results[env["name"]] = {"error": str(e)}
    
    return results


if __name__ == "__main__":
    # If running directly, test the local environment
    tester = MashaaerTester()
    tester.run_all_tests()