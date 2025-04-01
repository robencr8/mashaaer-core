import logging
import os
import json
import re
from collections import defaultdict

class IntentClassifier:
    """Classifies user intents based on text input"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define basic intents and their patterns
        self.intents = {
            "greeting": [
                r"hello", r"hi there", r"hey", r"greetings", r"good morning", 
                r"good afternoon", r"good evening", r"^hi$"
            ],
            "farewell": [
                r"goodbye", r"bye", r"see you", r"later", r"have a good day",
                r"good night", r"farewell"
            ],
            "gratitude": [
                r"thank you", r"thanks", r"appreciate it", r"grateful"
            ],
            "help": [
                r"help", r"assist", r"support", r"how do I", r"how to"
            ],
            "weather": [
                r"weather", r"forecast", r"temperature", r"raining", r"sunny"
            ],
            "time": [
                r"time is it", r"current time", r"what time", r"clock"
            ],
            "music": [
                r"play music", r"song", r"playlist", r"audio", r"listen to"
            ],
            "news": [
                r"news", r"headlines", r"current events", r"latest stories"
            ],
            "search": [
                r"search for", r"find", r"look up", r"google", r"information about"
            ],
            "schedule": [
                r"schedule", r"appointment", r"meeting", r"calendar", r"reminder", r"remind me"
            ],
            "joke": [
                r"joke", r"funny", r"make me laugh", r"tell me something funny"
            ],
            "fact": [
                r"fact", r"interesting", r"tell me about", r"did you know"
            ],
            "command": [
                r"turn on", r"turn off", r"open", r"close", r"start", r"stop"
            ]
        }
        
        # Compile regular expressions for faster matching
        self.compiled_patterns = {}
        for intent, patterns in self.intents.items():
            self.compiled_patterns[intent] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        
        # Path for saving/loading custom intents
        self.intents_path = "intent_data"
        os.makedirs(self.intents_path, exist_ok=True)
        self.custom_intents_file = os.path.join(self.intents_path, "custom_intents.json")
        
        # Load custom intents if file exists
        self._load_custom_intents()
    
    def initialize(self):
        """Initialize the intent classifier"""
        self.logger.info("Initializing intent classifier...")
        
        # Make sure we have a custom intents file
        if not os.path.exists(self.custom_intents_file):
            with open(self.custom_intents_file, 'w') as f:
                json.dump({}, f)
        
        self.logger.info("Intent classifier initialized")
    
    def _load_custom_intents(self):
        """Load custom intents from file"""
        if os.path.exists(self.custom_intents_file):
            try:
                with open(self.custom_intents_file, 'r') as f:
                    custom_intents = json.load(f)
                
                # Add custom intents to the existing ones
                for intent, patterns in custom_intents.items():
                    if intent not in self.intents:
                        self.intents[intent] = []
                    
                    self.intents[intent].extend(patterns)
                    
                    # Update compiled patterns
                    if intent not in self.compiled_patterns:
                        self.compiled_patterns[intent] = []
                    
                    self.compiled_patterns[intent].extend([
                        re.compile(pattern, re.IGNORECASE) for pattern in patterns
                    ])
                
                self.logger.info(f"Loaded {len(custom_intents)} custom intents")
            
            except Exception as e:
                self.logger.error(f"Failed to load custom intents: {str(e)}")
    
    def classify(self, text):
        """Classify the intent of the given text"""
        if not text:
            return "unknown"
        
        # Check each intent's patterns
        matches = defaultdict(int)
        
        for intent, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    matches[intent] += 1
        
        # Return the intent with the most matches
        if matches:
            best_intent = max(matches.items(), key=lambda x: x[1])[0]
            return best_intent
        
        return "unknown"
    
    def add_custom_intent(self, intent_name, patterns):
        """Add a custom intent with new patterns"""
        try:
            # Load existing custom intents
            custom_intents = {}
            if os.path.exists(self.custom_intents_file):
                with open(self.custom_intents_file, 'r') as f:
                    custom_intents = json.load(f)
            
            # Add or update the intent
            if intent_name not in custom_intents:
                custom_intents[intent_name] = []
            
            # Add new patterns
            custom_intents[intent_name].extend(patterns)
            
            # Save back to file
            with open(self.custom_intents_file, 'w') as f:
                json.dump(custom_intents, f, indent=2)
            
            # Update in-memory patterns
            if intent_name not in self.intents:
                self.intents[intent_name] = []
            
            self.intents[intent_name].extend(patterns)
            
            # Update compiled patterns
            if intent_name not in self.compiled_patterns:
                self.compiled_patterns[intent_name] = []
            
            self.compiled_patterns[intent_name].extend([
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ])
            
            self.logger.info(f"Added custom intent: {intent_name} with {len(patterns)} patterns")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to add custom intent: {str(e)}")
            return False
