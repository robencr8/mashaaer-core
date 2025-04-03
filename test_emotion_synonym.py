#!/usr/bin/env python3
"""
Test script for the enhanced Emotion Tracker with synonym handling
Tests various input texts and synonym detection capabilities
"""

import os
import json
from config import Config
from database.db_manager import DatabaseManager
from emotion_tracker import EmotionTracker

def main():
    # Initialize dependencies
    config = Config()
    # Force offline mode to skip OpenAI API calls
    config.OFFLINE_MODE = True
    db_manager = DatabaseManager(config)
    emotion_tracker = EmotionTracker(db_manager)
    
    # Ensure we're not going to use OpenAI for analysis
    emotion_tracker.openai_client = None
    
    # Test suite: samples specifically designed to test synonym detection
    test_cases = [
        {
            "text": "I'm feeling melancholy today",  # Synonym of sad
            "expected_primary": "sad"
        },
        {
            "text": "I'm ecstatic about my promotion",  # Synonym of happy/excited
            "expected_primary": "happy"
        },
        {
            "text": "The new policy is infuriating",  # Synonym of angry
            "expected_primary": "angry"
        },
        {
            "text": "I'm pondering the meaning of life",  # Synonym of contemplative
            "expected_primary": "contemplative"
        },
        {
            "text": "The speaker was utterly captivating",  # Synonym of interesting
            "expected_primary": "interested"
        },
        {
            "text": "I feel dejected after the rejection",  # Deeper synonym of sad
            "expected_primary": "sad"
        },
        {
            "text": "The documentary was enlightening",  # Synonym of inspiring
            "expected_primary": "inspired"
        }
    ]
    
    print("\n---- Testing Emotion Tracker with Synonym Detection ----\n")
    
    success_count = 0
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: '{test['text']}'")
        
        # Use the rule-based approach directly (bypass OpenAI)
        result = emotion_tracker._analyze_with_rules(test["text"])
        
        # Extract the primary emotion
        if isinstance(result, dict):
            primary = result.get("primary_emotion", "unknown")
            all_emotions = result.get("emotions", {})
            print(f"  Result: {primary}")
            print(f"  All emotions: {list(all_emotions.keys())[:3]} (top 3 of {len(all_emotions)})")
            if primary == test["expected_primary"]:
                print(f"  ✅ SUCCESS: Got expected emotion '{test['expected_primary']}'")
                success_count += 1
            else:
                print(f"  ❌ FAIL: Expected '{test['expected_primary']}', got '{primary}'")
                # Show emotion scores for debugging
                for emotion, score in sorted(all_emotions.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"    - {emotion}: {score:.4f}")
        else:
            primary = result  # String result
            print(f"  Result: {primary}")
            if primary == test["expected_primary"]:
                print(f"  ✅ SUCCESS: Got expected emotion '{test['expected_primary']}'")
                success_count += 1
            else:
                print(f"  ❌ FAIL: Expected '{test['expected_primary']}', got '{primary}'")
        
        print()
    
    # Print summary
    total = len(test_cases)
    print(f"\nSummary: {success_count}/{total} tests passed ({success_count/total*100:.1f}%)")
    if success_count == total:
        print("🎉 All tests passed! Synonym detection is working correctly.")
    else:
        print(f"⚠️ {total-success_count} tests failed. Review the issues above.")

if __name__ == "__main__":
    main()