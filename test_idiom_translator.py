"""
Test script for the Multilingual Emotion Idiom Translator
"""
import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base URL for API
BASE_URL = "http://localhost:5000/api/idioms"

def test_get_supported_languages():
    """Test the supported languages endpoint"""
    url = f"{BASE_URL}/languages"
    logger.info(f"Testing GET {url}")
    
    response = requests.get(url)
    logger.info(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        logger.info(f"Supported languages: {json.dumps(data, indent=2)}")
        return True
    else:
        logger.error(f"Failed to get supported languages: {response.text}")
        return False

def test_get_common_idioms():
    """Test the common idioms endpoint for English and Arabic"""
    languages = ["en", "ar"]
    emotions = ["happy", "sad", None]
    
    success = True
    
    for lang in languages:
        for emotion in emotions:
            url = f"{BASE_URL}/common?language={lang}"
            if emotion:
                url += f"&emotion={emotion}"
            
            logger.info(f"Testing GET {url}")
            
            response = requests.get(url)
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Common {emotion or 'general'} idioms for {lang}: {len(data.get('idioms', []))} found")
                if data.get('idioms'):
                    logger.info(f"Sample idiom: {json.dumps(data['idioms'][0], indent=2)}")
            else:
                logger.error(f"Failed to get common idioms: {response.text}")
                success = False
            
            # Avoid rate limiting
            time.sleep(1)
    
    return success

def test_translate_idiom():
    """Test the idiom translation endpoint"""
    test_cases = [
        {
            "idiom": "Walking on sunshine",
            "source_lang": "en",
            "target_lang": "ar",
            "emotion": "happy",
            "provide_explanation": True
        },
        {
            "idiom": "أسير على أشعة الشمس",
            "source_lang": "ar",
            "target_lang": "en",
            "emotion": "happy",
            "provide_explanation": True
        },
        {
            "idiom": "Feeling under the weather",
            "source_lang": "en",
            "target_lang": "ar",
            "emotion": "sad",
            "provide_explanation": False
        }
    ]
    
    success = True
    
    for tc in test_cases:
        url = f"{BASE_URL}/translate"
        logger.info(f"Testing POST {url} with data: {json.dumps(tc)}")
        
        response = requests.post(url, json=tc)
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Translation result: {json.dumps(data, indent=2)}")
        else:
            logger.error(f"Failed to translate idiom: {response.text}")
            success = False
        
        # Avoid rate limiting
        time.sleep(1)
    
    return success

def run_all_tests():
    """Run all tests and report results"""
    tests = [
        ("Get supported languages", test_get_supported_languages),
        ("Get common idioms", test_get_common_idioms),
        ("Translate idioms", test_translate_idiom)
    ]
    
    logger.info("Starting idiom translator API tests")
    
    results = {}
    all_passed = True
    
    for name, test_func in tests:
        logger.info(f"Running test: {name}")
        try:
            result = test_func()
            results[name] = "PASS" if result else "FAIL"
            if not result:
                all_passed = False
        except Exception as e:
            logger.error(f"Test {name} raised exception: {str(e)}")
            results[name] = "ERROR"
            all_passed = False
        
        logger.info(f"Test {name}: {results[name]}")
        logger.info("-" * 50)
    
    logger.info("Test results summary:")
    for name, result in results.items():
        logger.info(f"{name}: {result}")
    
    logger.info(f"Overall result: {'PASS' if all_passed else 'FAIL'}")
    return all_passed

if __name__ == "__main__":
    run_all_tests()