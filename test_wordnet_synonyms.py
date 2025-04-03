#!/usr/bin/env python3
"""
Test script to verify the WordNet synonym retrieval function.
"""

import os
import sys
import nltk
from nltk.corpus import wordnet as wn

# Make sure wordnet data is available
nltk.download('wordnet')

def get_synonyms(keyword, depth=1):
    """
    Get synonyms for a word using WordNet, with depth control.
    
    Args:
        keyword: The word to find synonyms for
        depth: How deep to go (1: direct synonyms, 2: synonyms of synonyms)
        
    Returns:
        List of synonyms
    """
    # Convert to lowercase for better matching
    keyword = keyword.lower()
    
    # Try to find synsets (synonym sets) for the word
    synsets = wn.synsets(keyword)
    
    # Collect all lemmas (word forms)
    synonyms = set()
    for synset in synsets:
        for lemma in synset.lemmas():
            synonym = lemma.name().lower().replace('_', ' ')
            if synonym != keyword:  # Don't include the original word
                synonyms.add(synonym)
    
    # For depth > 1, also get synonyms of synonyms
    if depth > 1 and synonyms:
        # Make a copy of the first-level synonyms
        first_level = set(synonyms)
        for word in first_level:
            # Find synonyms of this synonym
            for syn_synset in wn.synsets(word):
                for lemma in syn_synset.lemmas():
                    synonym = lemma.name().lower().replace('_', ' ')
                    # Don't include original or first-level synonyms
                    if synonym != keyword and synonym not in first_level:
                        synonyms.add(synonym)
    
    return list(synonyms)

def main():
    test_words = [
        # Format: (word, related_emotion, expected_synonym)
        ("melancholy", "sad", "sad"),
        ("ecstatic", "happy", "happy"),
        ("infuriating", "angry", "anger"),
        ("pondering", "contemplative", "reflective"),
        ("captivating", "interested", "fascinating"),
        ("dejected", "sad", "sad"),
        ("enlightening", "inspired", "inspiring")
    ]
    
    print("\n===== Testing WordNet Synonym Retrieval =====\n")
    
    for word, emotion, expected in test_words:
        print(f"Testing word: '{word}' (expected to be related to '{emotion}')")
        
        # Get direct synonyms (depth 1)
        direct_synonyms = get_synonyms(word, depth=1)
        print(f"  Direct synonyms (depth=1): {', '.join(direct_synonyms[:10])}..." if len(direct_synonyms) > 10 else f"  Direct synonyms: {', '.join(direct_synonyms)}")
        
        # Get deeper synonyms (depth 2)
        deeper_synonyms = get_synonyms(word, depth=2)
        print(f"  Deeper synonyms (depth=2): {', '.join(deeper_synonyms[:10])}..." if len(deeper_synonyms) > 10 else f"  Deeper synonyms: {', '.join(deeper_synonyms)}")
        
        # Check if expected synonym is found
        if expected in direct_synonyms:
            print(f"  ✅ SUCCESS: Found '{expected}' in direct synonyms")
        elif expected in deeper_synonyms:
            print(f"  ✅ SUCCESS: Found '{expected}' in deeper synonyms")
        else:
            print(f"  ❌ FAIL: Did not find '{expected}' in synonyms")
            # Suggest closest matches
            matches = [s for s in deeper_synonyms if expected in s or s in expected]
            if matches:
                print(f"  Closest matches: {', '.join(matches)}")
        
        print()

if __name__ == "__main__":
    main()