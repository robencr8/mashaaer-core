#!/usr/bin/env python3
"""
Test script for enhanced emotion synonym detection with emotion context.
This script tests the improved _get_synonyms function with emotion-specific context.
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure NLTK data is available
import nltk
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    logger.info("Downloading WordNet")
    nltk.download('wordnet')

from nltk.corpus import wordnet

# Cache for storing previously fetched synonyms
_synonym_cache = {}

def get_synonyms(keyword: str, depth: int = 1, emotion_context: str = None) -> List[str]:
    """
    Fetches synonyms for a given keyword using WordNet, with optional depth control.
    Also includes emotion-specific association dictionary to capture emotional connections
    not present in WordNet.

    Args:
        keyword: The word to find synonyms for.
        depth: The level of synonym retrieval (1: direct synonyms, 2: synonyms of synonyms, etc.).
        emotion_context: Optional related emotion for better context-aware synonyms.

    Returns:
        A list of synonyms for the keyword.
    """
    # Create a cache key that includes the emotion_context
    cache_key = f"{keyword}_{depth}_{emotion_context if emotion_context else 'none'}"
    if cache_key in _synonym_cache:
        return _synonym_cache[cache_key]
        
    # Custom emotion-related synonym mappings not captured well by WordNet
    emotion_synonyms = {
        "melancholy": ["sad", "unhappy", "sorrowful", "depressed", "gloomy"],
        "melancholic": ["sad", "unhappy", "sorrowful", "depressed", "gloomy"],
        "ecstatic": ["happy", "joyful", "delighted", "thrilled", "overjoyed"],
        "infuriating": ["angry", "enraging", "rage-inducing", "frustrating"],
        "frustrating": ["angry", "annoying", "irritating"],
        "pondering": ["contemplative", "thoughtful", "reflective", "meditative"],
        "thought-provoking": ["contemplative", "thoughtful", "reflective"],
        "captivating": ["interesting", "intriguing", "engaging", "fascinating"],
        "fascinating": ["interesting", "intriguing", "engaging"],
        "dejected": ["sad", "unhappy", "downcast", "disheartened", "depressed"],
        "enlightening": ["inspiring", "insightful", "thought-provoking", "illuminating"],
        "illuminating": ["inspiring", "insightful", "eye-opening"]
    }
    
    # Add emotion-specific words based on context
    if emotion_context:
        emotion_specific = {
            "happy": ["joy", "delight", "pleased", "content", "jubilant", "elated", "cheerful", "ecstatic"],
            "sad": ["unhappy", "depressed", "downcast", "glum", "melancholy", "sorrowful", "dejected"],
            "angry": ["mad", "irate", "infuriated", "enraged", "furious", "outraged", "annoyed"],
            "fearful": ["scared", "afraid", "frightened", "terrified", "alarmed", "anxious"],
            "interested": ["intrigued", "curious", "fascinated", "captivated", "engaged"],
            "inspired": ["motivated", "stimulated", "uplifted", "encouraged", "energized", "enlightened"],
            "contemplative": ["thoughtful", "reflective", "meditative", "pensive", "musing", "pondering"],
            "frustrated": ["annoyed", "irritated", "exasperated", "thwarted", "defeated"]
        }
        # Get the specific emotion words if available
        specific_syns = set(emotion_specific.get(emotion_context, []))
    else:
        specific_syns = set()
    
    # Get the custom emotion synonyms for this word if available
    custom_syns = set(emotion_synonyms.get(keyword.lower(), []))
    
    # Get WordNet synonyms
    wn_synonyms = set()
    queue = [(keyword, 0)]  # (word, current_depth)

    while queue:
        word, current_depth = queue.pop(0)
        if current_depth > depth:
            break

        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                wn_synonyms.add(lemma.name().replace('_', ' '))

            if current_depth < depth:
                # Add next level synonyms to the queue
                for lemma in syn.lemmas():
                    if lemma.name() != word:  # Avoid cycles
                        queue.append((lemma.name(), current_depth + 1))
    
    # Combine all synonym sources
    all_synonyms = wn_synonyms.union(custom_syns).union(specific_syns)
    
    # Remove the original keyword
    if keyword.lower() in all_synonyms:
        all_synonyms.remove(keyword.lower())
    
    # Cache the results
    result = list(all_synonyms)
    _synonym_cache[cache_key] = result
    return result

def main():
    """Test synonyms with emotion context"""
    test_words = [
        "happy", 
        "sad", 
        "melancholy", 
        "pondering", 
        "captivating", 
        "frustrated", 
        "ecstatic",
        "illuminating"
    ]
    
    test_contexts = [None, "happy", "sad", "contemplative", "angry", "interested"]
    
    for word in test_words:
        print(f"\n----- Synonyms for '{word}' -----")
        
        # Without context
        standard_syns = get_synonyms(word, depth=1)
        print(f"Without context (depth=1): {standard_syns[:10]}" + 
              (f" + {len(standard_syns)-10} more" if len(standard_syns) > 10 else ""))
              
        # With depth=2
        depth2_syns = get_synonyms(word, depth=2)
        print(f"Without context (depth=2): {depth2_syns[:10]}" + 
              (f" + {len(depth2_syns)-10} more" if len(depth2_syns) > 10 else ""))
        
        # With different contexts
        for context in test_contexts:
            if context:
                context_syns = get_synonyms(word, depth=1, emotion_context=context)
                # Find unique synonyms due to the context
                context_unique = set(context_syns) - set(standard_syns)
                if context_unique:
                    print(f"With '{context}' context: Added {context_unique}")
    
    # Test specific tricky cases
    tricky_tests = [
        ("melancholy", "sad"),
        ("pondering", "contemplative"),
        ("fascinating", "interested"),
        ("ecstatic", "happy"),
        ("dejected", "sad"),
        ("illuminating", "inspired")
    ]
    
    print("\n\n----- Testing Tricky Emotion Mappings -----")
    for word, emotion in tricky_tests:
        print(f"\nTesting if '{word}' is associated with '{emotion}':")
        # Without emotion context
        standard_syns = get_synonyms(word, depth=1)
        # With emotion context
        context_syns = get_synonyms(word, depth=1, emotion_context=emotion)
        # Check if relation improved
        if emotion in context_syns and emotion not in standard_syns:
            print(f"✅ Success: '{emotion}' added due to context")
        elif emotion in standard_syns:
            print(f"✓ Already included: '{emotion}' was already in standard synonyms")
        else:
            print(f"❌ Failed: '{emotion}' not added even with context")
            
        # Check reverse association
        print(f"Checking reverse - if '{emotion}' is associated with '{word}':")
        reverse_std = get_synonyms(emotion, depth=1)
        reverse_ctx = get_synonyms(emotion, depth=1, emotion_context=word)
        if word in reverse_ctx and word not in reverse_std:
            print(f"✅ Success: '{word}' added due to context")
        elif word in reverse_std:
            print(f"✓ Already included: '{word}' was already in standard synonyms")
        else:
            print(f"❌ Failed: '{word}' not added even with context")

if __name__ == "__main__":
    main()