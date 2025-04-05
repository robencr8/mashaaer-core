#!/usr/bin/env python3
"""
Advanced Mixed Emotion Testing Script

This script specifically tests the mixed emotion detection capabilities
of the Mashaaer Feelings emotion tracking system with enhanced patterns and detection.
"""
import json
import os
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add root directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from emotion_tracker import EmotionTracker
    from database.db_manager import DatabaseManager
except ImportError as e:
    print(f"Error importing required modules: {e}")
    sys.exit(1)

# Define test cases specifically focused on mixed emotions
MIXED_EMOTION_TEST_CASES = [
    # Classic mixed emotion cases
    {
        "phrase": "While I am excited about the new project, I am also nervous about the tight deadline",
        "expected": "mixed",
        "expected_emotions": ["excited", "nervous"]
    },
    {
        "phrase": "The bittersweet feeling of graduating - proud of my accomplishments but sad to leave friends behind",
        "expected": "mixed",
        "expected_emotions": ["proud", "sad"]
    },
    {
        "phrase": "I feel both happy that I won and sorry for my opponent",
        "expected": "mixed",
        "expected_emotions": ["happy", "sad"]
    },
    {
        "phrase": "It's a bittersweet moment, finishing this chapter of my life",
        "expected": "mixed",
        "expected_emotions": ["happy", "sad"]
    },
    
    # Subtle mixed emotions
    {
        "phrase": "Looking at old photos makes me smile and sigh at the same time",
        "expected": "mixed",
        "expected_emotions": ["happy", "sad"]
    },
    {
        "phrase": "The movie had me laughing through my tears",
        "expected": "mixed",
        "expected_emotions": ["happy", "sad"]
    },
    {
        "phrase": "The promotion means moving to a new city, which is exciting but also scary",
        "expected": "mixed",
        "expected_emotions": ["excited", "fearful"]
    },
    
    # Context-dependent mixed emotions
    {
        "phrase": "Leaving the job I've had for ten years. A new opportunity awaits, but I'll miss my colleagues.",
        "expected": "mixed",
        "expected_emotions": ["excited", "sad"]
    },
    {
        "phrase": "I achieved my goal, but the journey was so difficult that I'm not sure it was worth it",
        "expected": "mixed",
        "expected_emotions": ["satisfied", "frustrated"]
    },
    
    # Implicit mixed emotions (no explicit emotional terms)
    {
        "phrase": "Saying goodbye at the airport, we promised to stay in touch",
        "expected": "mixed",
        "expected_emotions": ["sad", "hopeful"]
    },
    {
        "phrase": "Walking across the stage to receive my diploma, I thought about all the years of hard work and the unknown future ahead",
        "expected": "mixed",
        "expected_emotions": ["proud", "anxious"]
    },
    
    # Complex mixed emotions
    {
        "phrase": "I'm grateful for the opportunity but frustrated by the limited resources and anxious about the outcome",
        "expected": "mixed",
        "expected_emotions": ["grateful", "frustrated", "anxious"]
    },
    {
        "phrase": "Part of me wants to celebrate our success, part of me is worried about the increased expectations, and another part is already planning the next challenge",
        "expected": "mixed",
        "expected_emotions": ["happy", "anxious", "determined"]
    },
    
    # Culturally-specific mixed emotions
    {
        "phrase": "That was a real sweet sorrow, just like Shakespeare described",
        "expected": "mixed",
        "expected_emotions": ["happy", "sad"]
    },
    {
        "phrase": "It's the kind of melancholic joy that comes with autumn",
        "expected": "mixed",
        "expected_emotions": ["happy", "sad"]
    },
    
    # Temporal mixed emotions
    {
        "phrase": "I started the day excited about the presentation, but now I'm just relieved it's over",
        "expected": "mixed",
        "expected_emotions": ["excited", "relieved"]
    },
    {
        "phrase": "Initially I was disappointed by the feedback, but now I'm motivated to improve",
        "expected": "mixed",
        "expected_emotions": ["disappointed", "inspired"]
    },
    
    # Contrasting mixed emotions with non-mixed emotions for validation
    {
        "phrase": "I'm absolutely thrilled about getting the job offer!",
        "expected": "happy",
        "expected_emotions": ["happy", "excited"]
    },
    {
        "phrase": "The news about the layoffs has me very worried about the future",
        "expected": "fearful",
        "expected_emotions": ["fearful", "anxious"]
    },
    {
        "phrase": "I'm just completely frustrated with this broken software",
        "expected": "frustrated",
        "expected_emotions": ["frustrated", "angry"]
    }
]

def run_tests(emotion_tracker: EmotionTracker) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Run all test cases and evaluate the emotion detection system
    
    Args:
        emotion_tracker: The EmotionTracker instance to test
        
    Returns:
        Tuple containing:
        - List of test results with detailed information
        - Statistics about the test run
    """
    results = []
    
    # Statistics tracking
    stats = {
        "total": len(MIXED_EMOTION_TEST_CASES),
        "correct": 0,
        "wrong": 0,
        "mixed_correct": 0,
        "mixed_wrong": 0,
        "non_mixed_correct": 0,
        "non_mixed_wrong": 0
    }
    
    start_time = time.time()
    
    for test_case in MIXED_EMOTION_TEST_CASES:
        phrase = test_case["phrase"]
        expected = test_case["expected"]
        expected_emotions = test_case.get("expected_emotions", [])
        
        # Skip OpenAI test to avoid quota issues - use only rule-based system
        # openai_result = emotion_tracker._analyze_with_openai(phrase)
        openai_result = None  # Skip OpenAI test
        
        # Analyze using rule-based system
        rule_result = emotion_tracker._analyze_with_rules(phrase)
        
        # Since we're skipping OpenAI, the combined method will just use rule-based
        # Let's explicitly tell it to skip OpenAI
        # Monkey patch the _analyze_with_openai method temporarily
        original_openai_method = emotion_tracker._analyze_with_openai
        emotion_tracker._analyze_with_openai = lambda x, context=None: None
        combined_result = emotion_tracker.analyze_text_advanced(phrase)
        emotion_tracker._analyze_with_openai = original_openai_method
        
        # Direct analyze_text method for simplicity (also patched)
        simple_result = emotion_tracker.analyze_text(phrase, return_details=True)
        
        # Extract the primary emotion from each result
        detected_openai = "skipped"  # Skip OpenAI test
        detected_rule = rule_result["primary_emotion"]
        detected_combined = combined_result["primary_emotion"]
        detected_simple = simple_result["primary_emotion"] if isinstance(simple_result, dict) else simple_result
        
        # Determine correctness (does the primary emotion match expected?)
        is_correct_openai = False  # Skip OpenAI test
        is_correct_rule = (expected == detected_rule)
        is_correct_combined = (expected == detected_combined)
        is_correct_simple = (expected == detected_simple)
        
        # Update statistics
        if expected == "mixed":
            if is_correct_combined:
                stats["mixed_correct"] += 1
            else:
                stats["mixed_wrong"] += 1
        else:
            if is_correct_combined:
                stats["non_mixed_correct"] += 1
            else:
                stats["non_mixed_wrong"] += 1
                
        if is_correct_combined:
            stats["correct"] += 1
        else:
            stats["wrong"] += 1
        
        # Get the top emotions detected
        top_emotions_combined = sorted(combined_result["emotions"].items(), key=lambda x: x[1], reverse=True)
        top_emotions_combined = [e for e, s in top_emotions_combined if e != "mixed"][:3]
        
        # Check if expected emotions were among top detected (for mixed emotions)
        expected_emotions_match = []
        for expected_emotion in expected_emotions:
            found = False
            for detected in top_emotions_combined:
                # Check for close matches (e.g., "happy" matches "excited", etc.)
                if _emotions_are_equivalent(expected_emotion, detected):
                    found = True
                    break
            expected_emotions_match.append(found)
        
        expected_emotions_match_rate = sum(expected_emotions_match) / len(expected_emotions_match) if expected_emotions_match else 0
        
        # Assemble detailed result
        result = {
            "phrase": phrase,
            "expected": expected,
            "expected_emotions": expected_emotions,
            "detected": detected_combined,
            "correct": is_correct_combined,
            "openai": {
                "detected": detected_openai, 
                "correct": is_correct_openai,
                "available": openai_result is not None
            },
            "rule": {
                "detected": detected_rule,
                "correct": is_correct_rule
            },
            "simple": {
                "detected": detected_simple,
                "correct": is_correct_simple
            },
            "emotions": combined_result["emotions"],
            "intensity": combined_result["intensity"],
            "expected_emotions_match_rate": expected_emotions_match_rate,
            "top_emotions": top_emotions_combined
        }
        
        # Add metadata if available in the result
        if "metadata" in combined_result:
            result["metadata"] = combined_result["metadata"]
        
        # Add to results list
        results.append(result)
        
        # Print progress
        print(f"Tested: '{phrase[:40]}...'")
        print(f"  Expected: {expected}, Detected: {detected_combined}, Correct: {is_correct_combined}")
        print(f"  Expected emotions: {expected_emotions}, Top detected: {top_emotions_combined}")
        print(f"  Match rate: {expected_emotions_match_rate:.2f}")
        print("-" * 80)
    
    end_time = time.time()
    
    # Add timing information
    stats["time_taken"] = end_time - start_time
    stats["accuracy"] = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
    stats["mixed_accuracy"] = stats["mixed_correct"] / (stats["mixed_correct"] + stats["mixed_wrong"]) if (stats["mixed_correct"] + stats["mixed_wrong"]) > 0 else 0
    stats["non_mixed_accuracy"] = stats["non_mixed_correct"] / (stats["non_mixed_correct"] + stats["non_mixed_wrong"]) if (stats["non_mixed_correct"] + stats["non_mixed_wrong"]) > 0 else 0
    
    return results, stats

def _emotions_are_equivalent(emotion1: str, emotion2: str) -> bool:
    """Check if two emotions are semantically equivalent or closely related
    
    Args:
        emotion1: First emotion name
        emotion2: Second emotion name
        
    Returns:
        True if emotions are equivalent or closely related
    """
    # Define groups of equivalent emotions
    equivalent_groups = [
        {"happy", "excited", "joy", "joyful"},
        {"sad", "disappointed", "melancholy"},
        {"fearful", "scared", "afraid", "anxious", "nervous"},
        {"angry", "frustrated", "mad", "annoyed"},
        {"surprised", "shocked", "astonished", "amazed"},
        {"disgusted", "repulsed"},
        {"calm", "relaxed", "peaceful", "serene"},
        {"proud", "accomplished", "confident"},
        {"grateful", "thankful", "appreciative"},
        {"inspired", "motivated", "determined", "hopeful"},
        {"confused", "uncertain", "unsure", "puzzled"},
        {"embarrassed", "humiliated", "ashamed"},
        {"bored", "disinterested", "uninterested"},
        {"tired", "exhausted", "fatigued"},
        {"satisfied", "content", "fulfilled"},
        {"lonely", "isolated", "abandoned"}
    ]
    
    # Check if emotions are in the same group
    for group in equivalent_groups:
        if emotion1 in group and emotion2 in group:
            return True
            
    # Also check exact match
    return emotion1 == emotion2

def save_results(results: List[Dict[str, Any]], stats: Dict[str, Any], filename: str = None) -> str:
    """
    Save test results to a JSON file
    
    Args:
        results: List of test results
        stats: Test run statistics
        filename: Optional filename to use
        
    Returns:
        Path to the saved file
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mixed_emotion_test_results_{timestamp}.json"
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "summary": stats,
        "results": results
    }
    
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
        
    return filename

def print_summary(stats: Dict[str, Any]) -> None:
    """
    Print a summary of the test results
    
    Args:
        stats: Test run statistics
    """
    print("\n" + "=" * 80)
    print(f"TEST SUMMARY")
    print("=" * 80)
    print(f"Total test cases: {stats['total']}")
    print(f"Overall accuracy: {stats['accuracy']:.2%}")
    print(f"Mixed emotion accuracy: {stats['mixed_accuracy']:.2%} ({stats['mixed_correct']}/{stats['mixed_correct'] + stats['mixed_wrong']})")
    print(f"Non-mixed emotion accuracy: {stats['non_mixed_accuracy']:.2%} ({stats['non_mixed_correct']}/{stats['non_mixed_correct'] + stats['non_mixed_wrong']})")
    print(f"Time taken: {stats['time_taken']:.2f} seconds")
    print("=" * 80)

def main():
    """Main function to run mixed emotion tests"""
    print("Initializing test environment...")
    
    # Initialize DB manager and emotion tracker using direct database URL
    # This simpler approach bypasses the config module entirely
    import os
    db_url = os.environ.get("DATABASE_URL")
    
    print(f"Using database URL: {db_url}")
    
    # Create a simplified config object with the essential attributes
    class SimpleConfig:
        def __init__(self, db_url):
            self.DATABASE_URL = db_url
            self.USE_POSTGRES = True if db_url and db_url.startswith("postgresql") else False
    
    config_obj = SimpleConfig(db_url)
    db_manager = DatabaseManager(config_obj)
    emotion_tracker = EmotionTracker(db_manager)
    
    print(f"Running {len(MIXED_EMOTION_TEST_CASES)} mixed emotion test cases...")
    results, stats = run_tests(emotion_tracker)
    
    # Save results
    filename = save_results(results, stats)
    print(f"Results saved to {filename}")
    
    # Print summary
    print_summary(stats)

if __name__ == "__main__":
    main()