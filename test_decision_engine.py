#!/usr/bin/env python3
"""
Test script for the RobinDecisionEngine

Tests the rule matching logic, weight adjustments, and memory functionality
of the decision engine with various scenarios.
"""
import json
import logging
import unittest
import sys
from rule_engine import RobinDecisionEngine, Rule
from rules_config_loader import load_rules_from_config

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

class TestDecisionEngine(unittest.TestCase):
    """Test cases for the decision engine"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a decision engine with test rules
        self.engine = RobinDecisionEngine()
        
        # Add some test rules manually
        self.engine.add_rule(Rule(
            emotion="sad", 
            keyword="alone", 
            action="offer_companionship",
            weight=1.1,
            rule_id="test001"
        ))
        
        self.engine.add_rule(Rule(
            emotion="happy", 
            keyword="music", 
            action="play_music",
            params={"genre": "uplifting"},
            weight=1.5,
            rule_id="test002"
        ))
        
        self.engine.add_rule(Rule(
            emotion="angry", 
            keyword="frustrated", 
            action="suggest_calming",
            params={"technique": "breathing"},
            weight=1.3,
            rule_id="test003"
        ))
        
        # Log setup completion
        logging.info(f"Test setup complete with {len(self.engine.rules)} rules")
    
    def test_basic_rule_matching(self):
        """Test the basic rule matching functionality"""
        # Test with matching emotion and keyword
        result = self.engine.decide("I feel so alone today", "sad")
        self.assertEqual(result["action"], "offer_companionship")
        logging.info(f"Rule matching test 1 passed: {result}")
        
        # Test with matching keyword but different emotion
        result = self.engine.decide("I feel alone but happy", "happy")
        # This should not match the first rule because of emotion mismatch
        self.assertNotEqual(result["action"], "offer_companionship")
        logging.info(f"Rule matching test 2 passed: {result}")
        
        # Test with matching emotion but no keyword
        result = self.engine.decide("I feel so sad today", "sad")
        # This should not match any specific rule
        self.assertEqual(result["action"], "respond_normally")
        logging.info(f"Rule matching test 3 passed: {result}")
    
    def test_weight_based_selection(self):
        """Test that rules are selected based on weight when multiple match"""
        # Add another rule with the same trigger but lower weight
        self.engine.add_rule(Rule(
            emotion="sad", 
            keyword="alone", 
            action="suggest_activity",
            weight=0.5,
            rule_id="test004"
        ))
        
        # The higher weight rule should be selected
        result = self.engine.decide("I feel alone", "sad")
        self.assertEqual(result["action"], "offer_companionship")
        logging.info(f"Weight-based selection test passed: {result}")
    
    def test_rule_weight_adjustment(self):
        """Test rule weight adjustment functionality"""
        # Get initial weight
        initial_weight = None
        for rule in self.engine.rules:
            if getattr(rule, 'id', None) == "test001":
                initial_weight = rule.weight
                break
        
        # Update weight
        self.engine.update_rule_weight("test001", 0.2)
        
        # Verify weight was updated
        new_weight = None
        for rule in self.engine.rules:
            if getattr(rule, 'id', None) == "test001":
                new_weight = rule.weight
                break
        
        self.assertIsNotNone(initial_weight)
        self.assertIsNotNone(new_weight)
        self.assertEqual(new_weight, initial_weight + 0.2)
        logging.info(f"Weight adjustment test passed: {initial_weight} -> {new_weight}")
    
    def test_memory_storage(self):
        """Test the memory storage functionality"""
        # Store some test memories
        user_id = "test_user_123"
        self.engine.store_memory(user_id, "preferred_genre", "jazz")
        self.engine.store_memory(user_id, "last_mood", "happy")
        
        # Retrieve memories
        retrieved_genre = self.engine.get_memory(user_id, "preferred_genre")
        retrieved_mood = self.engine.get_memory(user_id, "last_mood")
        
        # Verify memories were stored correctly
        self.assertEqual(retrieved_genre, "jazz")
        self.assertEqual(retrieved_mood, "happy")
        logging.info(f"Memory storage test passed for user {user_id}")
        
        # Test retrieving non-existent memory
        missing_memory = self.engine.get_memory(user_id, "non_existent_key")
        self.assertIsNone(missing_memory)
        logging.info("Non-existent memory test passed")
        
        # Test retrieving memory for non-existent user
        missing_user_memory = self.engine.get_memory("non_existent_user", "preferred_genre")
        self.assertIsNone(missing_user_memory)
        logging.info("Non-existent user memory test passed")

    def test_config_loaded_rules(self):
        """Test rules loaded from config file"""
        # Load rules from config file
        config_engine = load_rules_from_config('rules_config.json')
        
        # Test a rule that should be in the config
        result = config_engine.decide("I feel alone", "sad")
        self.assertEqual(result["action"], "offer_companionship")
        logging.info(f"Config-loaded rule test 1 passed: {result}")
        
        # Test another rule from config
        result = config_engine.decide("I love music", "happy")
        self.assertEqual(result["action"], "play_music")
        self.assertEqual(result["params"].get("genre"), "uplifting")
        logging.info(f"Config-loaded rule test 2 passed: {result}")
        
        # Test a more complex rule
        result = config_engine.decide("I'm so frustrated with this", "angry")
        self.assertEqual(result["action"], "suggest_calming")
        self.assertEqual(result["params"].get("technique"), "breathing")
        logging.info(f"Config-loaded rule test 3 passed: {result}")
        
        # Test the Arabic rules
        result = config_engine.decide("أشعر وحيد", "sad")
        self.assertEqual(result["action"], "offer_companionship")
        logging.info(f"Arabic rule test passed: {result}")

def run_tests():
    """Run the tests"""
    unittest.main()

def run_interactive_test():
    """Run an interactive test of the decision engine"""
    logging.info("Loading rules from config...")
    engine = load_rules_from_config('rules_config.json')
    
    # Print loaded rules
    logging.info(f"Loaded {len(engine.rules)} rules from config:")
    for i, rule in enumerate(engine.rules, 1):
        logging.info(f"{i}. {rule}")
    
    print("\nEnter 'q' to quit\n")
    while True:
        # Get user input
        text = input("\nEnter your message: ")
        if text.lower() == 'q':
            break
        
        # Get emotion
        emotion = input("Enter emotion (or leave blank for auto-detection): ")
        if not emotion:
            emotion = "neutral"  # Simple default
        
        # Process message
        result = engine.decide(text, emotion)
        
        # Display result
        print("\nDecision Engine Result:")
        print(f"- Action: {result['action']}")
        if result.get('params'):
            print(f"- Parameters: {result['params']}")
        print("")

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive_test()
    else:
        run_tests()