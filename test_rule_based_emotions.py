#!/usr/bin/env python3
"""
Simplified Mixed Emotion Testing Script (Rule-Based Only)

This script specifically tests the rule-based mixed emotion detection capabilities
of the Mashaaer Feelings emotion tracking system.
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
        "expected_emotions": ["happy", "fearful"]
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
        "expected_emotions": ["happy", "fearful"]
    },
    
    # Context-dependent mixed emotions
    {
        "phrase": "Leaving the job I've had for ten years. A new opportunity awaits, but I'll miss my colleagues.",
        "expected": "mixed",
        "expected_emotions": ["happy", "sad"]
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

def test_rule_based_only():
    """Test only the rule-based emotion detection"""
    print("Creating EmotionTracker for rule-based testing...")
    
    # Get database connection
    import os
    db_url = os.environ.get("DATABASE_URL")
    
    # Create a simplified config object
    class SimpleConfig:
        def __init__(self, db_url):
            self.DATABASE_URL = db_url
            self.USE_POSTGRES = True if db_url and db_url.startswith("postgresql") else False
    
    config_obj = SimpleConfig(db_url)
    db_manager = DatabaseManager(config_obj)
    
    # Import EmotionTracker here to modify it
    from emotion_tracker import EmotionTracker
    
    # Create a subclass that overrides the OpenAI method
    class RuleBasedEmotionTracker(EmotionTracker):
        def _analyze_with_openai(self, text, context=None):
            """Override to always return None"""
            return None
        
        def analyze_text_advanced(self, text, context=None):
            """Override to use only rule-based system"""
            # Use rule-based analysis only
            result = self._analyze_with_rules(text, context)
            return result
    
    # Create our modified tracker
    emotion_tracker = RuleBasedEmotionTracker(db_manager)
    
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
    
    results = []
    
    print(f"Running {len(MIXED_EMOTION_TEST_CASES)} test cases...")
    start_time = time.time()
    
    for test_case in MIXED_EMOTION_TEST_CASES:
        phrase = test_case["phrase"]
        expected = test_case["expected"]
        expected_emotions = test_case.get("expected_emotions", [])
        
        # Get result from rule-based analysis
        result = emotion_tracker.analyze_text_advanced(phrase)
        detected = result["primary_emotion"]
        
        # Determine if correct
        is_correct = (expected == detected)
        
        # Update statistics
        if expected == "mixed":
            if is_correct:
                stats["mixed_correct"] += 1
            else:
                stats["mixed_wrong"] += 1
        else:
            if is_correct:
                stats["non_mixed_correct"] += 1
            else:
                stats["non_mixed_wrong"] += 1
        
        if is_correct:
            stats["correct"] += 1
        else:
            stats["wrong"] += 1
        
        # Get top emotions
        top_emotions = sorted(result["emotions"].items(), key=lambda x: x[1], reverse=True)
        top_emotions = [e for e, s in top_emotions if e != "mixed"][:3]
        
        # Check if expected emotions were among top detected
        expected_emotions_match = []
        for expected_emotion in expected_emotions:
            found = False
            for detected_emotion in top_emotions:
                # Check for equivalence (e.g., "happy" matches "excited")
                if are_emotions_equivalent(expected_emotion, detected_emotion):
                    found = True
                    break
            expected_emotions_match.append(found)
        
        match_rate = sum(expected_emotions_match) / len(expected_emotions_match) if expected_emotions_match else 0
        
        # Save result
        test_result = {
            "phrase": phrase,
            "expected": expected,
            "detected": detected,
            "correct": is_correct,
            "expected_emotions": expected_emotions,
            "top_emotions": top_emotions,
            "match_rate": match_rate,
            "emotions": result["emotions"],
            "intensity": result["intensity"]
        }
        
        # Add metadata if available
        if "metadata" in result:
            test_result["metadata"] = result["metadata"]
        
        results.append(test_result)
        
        # Print progress
        print(f"Tested: '{phrase[:50]}...'")
        print(f"  Expected: {expected}, Detected: {detected}, Correct: {is_correct}")
        print(f"  Expected emotions: {expected_emotions}, Top detected: {top_emotions}")
        print(f"  Match rate: {match_rate:.2f}")
        print("-" * 80)
    
    end_time = time.time()
    
    # Calculate statistics
    stats["time_taken"] = end_time - start_time
    stats["accuracy"] = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
    stats["mixed_accuracy"] = stats["mixed_correct"] / (stats["mixed_correct"] + stats["mixed_wrong"]) if (stats["mixed_correct"] + stats["mixed_wrong"]) > 0 else 0
    stats["non_mixed_accuracy"] = stats["non_mixed_correct"] / (stats["non_mixed_correct"] + stats["non_mixed_wrong"]) if (stats["non_mixed_correct"] + stats["non_mixed_wrong"]) > 0 else 0
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total test cases: {stats['total']}")
    print(f"Overall accuracy: {stats['accuracy']:.2%}")
    print(f"Mixed emotion accuracy: {stats['mixed_accuracy']:.2%} ({stats['mixed_correct']}/{stats['mixed_correct'] + stats['mixed_wrong']})")
    print(f"Non-mixed emotion accuracy: {stats['non_mixed_accuracy']:.2%} ({stats['non_mixed_correct']}/{stats['non_mixed_correct'] + stats['non_mixed_wrong']})")
    print(f"Time taken: {stats['time_taken']:.2f} seconds")
    print("=" * 80)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rule_based_test_results_{timestamp}.json"
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "summary": stats,
        "results": results
    }
    
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Results saved to {filename}")
    
    return stats, results

def are_emotions_equivalent(emotion1, emotion2):
    """Check if two emotions are semantically equivalent"""
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

if __name__ == "__main__":
    test_rule_based_only()