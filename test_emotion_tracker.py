#!/usr/bin/env python3
"""
Test script for enhanced emotion tracker functionality
"""
import json
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the emotion tracker
from emotion_tracker import EmotionTracker

# Mock database manager for testing
class MockDBManager:
    def __init__(self):
        self.log_calls = []
    
    def log_emotion(self, *args, **kwargs):
        self.log_calls.append(("log_emotion", args, kwargs))
        return True

# Test sentences for various emotions including the new ones
test_sentences = {
    "happy": "I am feeling so happy and excited today!",
    "sad": "I feel really sad about what happened yesterday.",
    "angry": "This makes me so angry, I can't believe it!",
    "fearful": "I'm really scared about the upcoming presentation.",
    "disgusted": "That food was disgusting, I couldn't eat it.",
    "surprised": "Wow! I didn't expect that at all!",
    "confused": "I'm not sure I understand what's happening here.",
    "interested": "This topic is really fascinating, I'd like to learn more.",
    "excited": "I can't wait for the concert this weekend!",
    "anxious": "I feel very anxious about the test results.",
    "calm": "I'm feeling very peaceful and relaxed now.",
    "tired": "I'm completely exhausted after the long day.",
    "bored": "There's nothing to do, I'm so bored.",
    "grateful": "I'm so thankful for all your help.",
    "hopeful": "I believe things will get better soon.",
    "lonely": "I miss having people around me.",
    "proud": "I accomplished my goal and I'm really proud of myself.",
    "embarrassed": "I made a mistake in front of everyone and felt so awkward.",
    # New emotion types
    "amused": "That joke was hilarious, I can't stop laughing!",
    "inspired": "After watching that documentary, I feel so motivated to create.",
    "satisfied": "The project is complete and it turned out exactly as planned.",
    "frustrated": "I've been trying to solve this problem for hours with no progress.",
    "contemplative": "I've been thinking deeply about the meaning of life lately."
}

# Phrases for testing emotional expressions
test_phrases = {
    "happy": "I'm having a great time with my friends",
    "sad": "My heart is heavy after hearing the news",
    "angry": "This situation is making my blood boil",
    "fearful": "I'm worried sick about the exam results",
    "amused": "That movie had me cracking up the whole time",
    "inspired": "This book gave me a burst of creativity",
    "satisfied": "The job is done and it checks all the boxes",
    "frustrated": "I feel like I'm hitting a wall with this project",
    "contemplative": "I'm lost in thought about what the future holds"
}

# Mixed emotions for complex analysis
mixed_emotions = [
    "I'm excited about the new job but also anxious about the challenges ahead.",
    "The movie made me laugh but the ending left me feeling sad and reflective.",
    "I'm proud of my work but frustrated it took so long to complete.",
    "I'm disappointed about the cancellation but hopeful we can reschedule soon.",
    "While I'm grateful for the opportunity, I'm tired from all the preparation."
]

def run_tests():
    """Run the emotion tracker tests"""
    logger.info("Starting emotion tracker tests")
    
    # Initialize the emotion tracker
    db_manager = MockDBManager()
    emotion_tracker = EmotionTracker(db_manager)
    
    # Set OpenAI availability to False to force rule-based analysis
    global OPENAI_AVAILABLE
    import emotion_tracker
    emotion_tracker.OPENAI_AVAILABLE = False
    
    # Test basic emotions
    logger.info("Testing basic emotions...")
    results = {}
    
    for emotion, sentence in test_sentences.items():
        result = emotion_tracker.analyze_text_advanced(sentence)
        primary = result.get("primary_emotion", "unknown")
        intensity = result.get("intensity", 0)
        confidence = result.get("metadata", {}).get("confidence", 0) if "metadata" in result else 0
        
        results[emotion] = {
            "sentence": sentence,
            "detected": primary,
            "intensity": intensity,
            "confidence": confidence,
            "match": primary == emotion
        }
        
        logger.info(f"Emotion: {emotion} -> Detected: {primary} (Intensity: {intensity:.2f}, Confidence: {confidence:.2f})")
    
    # Test emotional phrases
    logger.info("\nTesting emotional phrases...")
    phrase_results = {}
    
    for emotion, phrase in test_phrases.items():
        result = emotion_tracker.analyze_text_advanced(phrase)
        primary = result.get("primary_emotion", "unknown")
        intensity = result.get("intensity", 0)
        
        phrase_results[emotion] = {
            "phrase": phrase,
            "detected": primary,
            "intensity": intensity,
            "match": primary == emotion
        }
        
        logger.info(f"Phrase emotion: {emotion} -> Detected: {primary} (Intensity: {intensity:.2f})")
    
    # Test mixed emotions
    logger.info("\nTesting mixed emotions...")
    mixed_results = []
    
    for text in mixed_emotions:
        result = emotion_tracker.analyze_text_advanced(text)
        primary = result.get("primary_emotion", "unknown")
        emotions = result.get("emotions", {})
        intensity = result.get("intensity", 0)
        
        # Get top 3 emotions
        top_emotions = sorted([(e, s) for e, s in emotions.items()], key=lambda x: x[1], reverse=True)[:3]
        
        mixed_result = {
            "text": text,
            "primary": primary,
            "intensity": intensity,
            "top_emotions": top_emotions
        }
        mixed_results.append(mixed_result)
        
        top_emotions_str = ", ".join([f"{e}: {s:.2f}" for e, s in top_emotions])
        logger.info(f"Mixed: '{text[:50]}...' -> Primary: {primary}, Top emotions: {top_emotions_str}")
    
    # Generate summary
    correct_basic = sum(1 for r in results.values() if r["match"])
    accuracy = correct_basic / len(results) * 100 if results else 0
    
    correct_phrases = sum(1 for r in phrase_results.values() if r["match"])
    phrase_accuracy = correct_phrases / len(phrase_results) * 100 if phrase_results else 0
    
    logger.info("\n--- SUMMARY ---")
    logger.info(f"Basic emotions: {correct_basic}/{len(results)} correct ({accuracy:.1f}%)")
    logger.info(f"Emotional phrases: {correct_phrases}/{len(phrase_results)} correct ({phrase_accuracy:.1f}%)")
    logger.info(f"Mixed emotions: {len(mixed_results)} analyzed")
    
    # Save results to file
    output = {
        "timestamp": datetime.now().isoformat(),
        "basic_emotions": results,
        "emotional_phrases": phrase_results,
        "mixed_emotions": mixed_results,
        "summary": {
            "basic_accuracy": accuracy,
            "phrase_accuracy": phrase_accuracy
        }
    }
    
    with open("emotion_test_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"Results saved to emotion_test_results.json")
    
    return output

if __name__ == "__main__":
    run_tests()