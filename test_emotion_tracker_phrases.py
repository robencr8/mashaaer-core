from emotion_tracker import EmotionTracker
from database.db_manager import DatabaseManager
import os

def main():
    # Disable OpenAI for faster testing
    os.environ["OPENAI_API_KEY"] = ""
    
    db = DatabaseManager()
    et = EmotionTracker(db)
    
    test_phrases = [
        'I am absolutely ecstatic about the results',
        'I am feeling quite melancholy today',
        'The documentary was really thought-provoking',
        'The sunset was breathtaking and filled me with wonder',
        'I could not figure out how to solve the problem despite trying everything',
        'That was infuriating to deal with',
        'I found the movie captivating from start to finish'
    ]
    
    print("\n----- Testing Emotion Detection with Real-World Phrases -----\n")
    
    for phrase in test_phrases:
        result = et.analyze_text(phrase, return_details=True)
        primary_emotion = result["primary_emotion"]
        print(f'"{phrase}": {primary_emotion}')
    
if __name__ == "__main__":
    main()