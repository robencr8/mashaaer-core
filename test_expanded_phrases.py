from emotion_tracker import EmotionTracker
from database.db_manager import DatabaseManager
import os
import json
from datetime import datetime

def main():
    # Disable OpenAI for faster testing
    os.environ["OPENAI_API_KEY"] = ""
    
    db = DatabaseManager()
    et = EmotionTracker(db)
    
    test_phrases = [
        # Happy emotions
        {'text': 'I am absolutely ecstatic about the results', 'expected': 'happy'},
        {'text': 'This promotion has made my entire year!', 'expected': 'happy'},
        {'text': 'Seeing my family after so long brings me such joy', 'expected': 'happy'},
        
        # Sad emotions
        {'text': 'I am feeling quite melancholy today', 'expected': 'sad'},
        {'text': 'The news about the accident left me heartbroken', 'expected': 'sad'},
        {'text': 'I miss how things used to be before everything changed', 'expected': 'sad'},
        
        # Angry emotions
        {'text': 'That was infuriating to deal with', 'expected': 'angry'},
        {'text': 'I cannot believe they would lie to my face like that', 'expected': 'angry'},
        {'text': 'Their constant excuses are getting on my nerves', 'expected': 'angry'},
        
        # Fearful emotions
        {'text': 'The thought of speaking in front of everyone terrifies me', 'expected': 'fearful'},
        {'text': 'I keep having nightmares about failing the exam', 'expected': 'fearful'},
        {'text': 'Walking alone at night makes me feel unsafe', 'expected': 'fearful'},
        
        # Surprised emotions
        {'text': 'I never expected them to announce that today!', 'expected': 'surprised'},
        {'text': 'The plot twist completely caught me off guard', 'expected': 'surprised'},
        {'text': 'Finding out I won the competition was shocking', 'expected': 'surprised'},
        
        # Contemplative emotions
        {'text': 'The documentary was really thought-provoking', 'expected': 'contemplative'},
        {'text': 'I find myself reflecting on the meaning of success lately', 'expected': 'contemplative'},
        {'text': 'Her question made me reconsider my entire approach', 'expected': 'contemplative'},
        
        # Inspired emotions
        {'text': 'The sunset was breathtaking and filled me with wonder', 'expected': 'inspired'},
        {'text': 'Her story of overcoming obstacles motivated me to try again', 'expected': 'inspired'},
        {'text': 'The conference left me with so many new ideas to explore', 'expected': 'inspired'},
        
        # Frustrated emotions
        {'text': 'I could not figure out how to solve the problem despite trying everything', 'expected': 'frustrated'},
        {'text': 'The constant interruptions made it impossible to focus', 'expected': 'frustrated'},
        {'text': 'Every time I fix one issue, three more appear', 'expected': 'frustrated'},
        
        # Interested emotions
        {'text': 'I found the movie captivating from start to finish', 'expected': 'interested'},
        {'text': 'That research paper contains fascinating insights about the topic', 'expected': 'interested'},
        {'text': 'I cannot stop reading about ancient civilizations lately', 'expected': 'interested'},
        
        # More complex sentences with multiple emotions
        {'text': 'While I am excited about the new project, I am also nervous about the tight deadline', 'expected': 'mixed'},
        {'text': 'The bittersweet feeling of graduating - proud of my accomplishments but sad to leave friends behind', 'expected': 'mixed'}
    ]
    
    print("\n----- Testing Emotion Detection with Expanded Phrase Set -----\n")
    
    results = []
    correct_count = 0
    total_count = len(test_phrases)
    
    for test_case in test_phrases:
        phrase = test_case['text']
        expected = test_case['expected']
        
        result = et.analyze_text(phrase, return_details=True)
        primary_emotion = result["primary_emotion"]
        
        # For mixed emotions, just check if it detected multiple emotions
        if expected == 'mixed':
            emotions = result["emotions"]
            # Consider correct if at least 2 emotions have significant scores
            significant_emotions = sum(1 for score in emotions.values() if score > 0.2)
            is_correct = significant_emotions >= 2
        else:
            is_correct = primary_emotion == expected
        
        if is_correct:
            correct_count += 1
            status = "✓"
        else:
            status = "✗"
        
        print(f'{status} "{phrase[:60]}{"..." if len(phrase) > 60 else ""}": got {primary_emotion}, expected {expected}')
        
        results.append({
            'phrase': phrase,
            'expected': expected,
            'detected': primary_emotion,
            'correct': is_correct,
            'emotions': result["emotions"]
        })
    
    accuracy = (correct_count / total_count) * 100
    print(f"\nAccuracy: {correct_count}/{total_count} ({accuracy:.1f}%)")
    
    # Print summarized results by emotion type
    emotions_accuracy = {}
    for emotion in set([r['expected'] for r in results if r['expected'] != 'mixed']):
        emotion_tests = [r for r in results if r['expected'] == emotion]
        correct = len([r for r in emotion_tests if r['correct']])
        total = len(emotion_tests)
        emotions_accuracy[emotion] = (correct, total, (correct / total * 100) if total > 0 else 0)
    
    print("\nAccuracy by emotion type:")
    for emotion, (correct, total, pct) in sorted(emotions_accuracy.items()):
        print(f"  {emotion}: {correct}/{total} ({pct:.1f}%)")
    
    # Save results to file for further analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"emotion_test_results_{timestamp}.json"
    
    with open(result_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'accuracy': accuracy,
            'results': results,
            'accuracy_by_emotion': {e: {'correct': c, 'total': t, 'percentage': p} 
                                   for e, (c, t, p) in emotions_accuracy.items()}
        }, f, indent=2)
    
    print(f"\nDetailed results saved to {result_file}")
    
if __name__ == "__main__":
    main()