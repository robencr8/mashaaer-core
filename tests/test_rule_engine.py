"""
Unit tests for the Rule Engine in Mashaaer Feelings Application
Tests rule matching, feedback processing, and response generation
"""
import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import patch

# Import modules to test
from rules_config_loader import RulesConfigLoader

class TestRuleEngine(unittest.TestCase):
    """Test cases for the rule engine"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test rules file
        self.test_rules_path = os.path.join(self.test_dir, 'test_rules.json')
        
        # Sample test rules
        self.test_rules = [
            {
                "id": "rule001",
                "emotion": "sad",
                "keyword": "alone",
                "action": "offer_companionship",
                "weight": 1.0
            },
            {
                "id": "rule002",
                "emotion": "happy",
                "keyword": "music",
                "action": "play_music",
                "params": {
                    "genre": "uplifting"
                },
                "weight": 1.5
            },
            {
                "id": "rule003",
                "emotion": "neutral",
                "keyword": "weather",
                "action": "fetch_weather",
                "weight": 1.2
            }
        ]
        
        # Write test rules to file
        with open(self.test_rules_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_rules, f, indent=2)
        
        # Initialize rule engine with test rules
        self.rules_loader = RulesConfigLoader(self.test_rules_path)
    
    def tearDown(self):
        """Clean up after each test"""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def test_load_rules(self):
        """Test loading rules from file"""
        # Verify that rules were loaded correctly
        rules = self.rules_loader.get_rules()
        
        # Check number of rules
        self.assertEqual(len(rules), 3, "Should load 3 rules")
        
        # Check specific rule content
        rule1 = self.rules_loader.get_rule_by_id('rule001')
        self.assertEqual(rule1['emotion'], 'sad')
        self.assertEqual(rule1['keyword'], 'alone')
        self.assertEqual(rule1['action'], 'offer_companionship')
    
    def test_match_rules(self):
        """Test matching rules based on emotion and message"""
        # Test matching a sad message
        sad_message = "I feel so alone today"
        sad_matches = self.rules_loader.match_rules('sad', sad_message)
        
        # Should match rule001
        self.assertEqual(len(sad_matches), 1, "Sad message should match 1 rule")
        self.assertEqual(sad_matches[0]['id'], 'rule001')
        
        # Test matching a happy message about music
        happy_message = "I'd love to listen to music"
        happy_matches = self.rules_loader.match_rules('happy', happy_message)
        
        # Should match rule002
        self.assertEqual(len(happy_matches), 1, "Happy music message should match 1 rule")
        self.assertEqual(happy_matches[0]['id'], 'rule002')
        
        # Test message that doesn't match any rule keywords
        no_match_message = "I'm thinking about the stars"
        no_matches = self.rules_loader.match_rules('neutral', no_match_message)
        
        # Should not match any rules
        self.assertEqual(len(no_matches), 0, "Message should not match any rules")
    
    def test_rule_sorting(self):
        """Test that rules are sorted by weight"""
        # Add a new rule with higher weight
        high_weight_rule = {
            "id": "rule004",
            "emotion": "sad",
            "keyword": "cry",
            "action": "offer_sympathy",
            "weight": 2.0
        }
        
        # Add rule to loader
        self.rules_loader.add_rule(high_weight_rule)
        
        # Get rules - should be sorted by weight
        sorted_rules = self.rules_loader.get_rules()
        
        # Highest weight rule should be first
        self.assertEqual(sorted_rules[0]['id'], 'rule004')
        self.assertEqual(sorted_rules[0]['weight'], 2.0)
    
    def test_adjust_rule_weight(self):
        """Test adjusting rule weights based on feedback"""
        # Get initial weight
        rule_id = 'rule001'
        initial_rule = self.rules_loader.get_rule_by_id(rule_id)
        initial_weight = initial_rule['weight']
        
        # Positive feedback should increase weight by 10%
        self.rules_loader.adjust_rule_weight(rule_id, 'positive')
        
        # Get updated weight
        updated_rule = self.rules_loader.get_rule_by_id(rule_id)
        updated_weight = updated_rule['weight']
        
        # Check that weight increased by 10%
        expected_weight = round(initial_weight * 1.1, 2)
        self.assertEqual(updated_weight, expected_weight)
        
        # Negative feedback should decrease weight by 10%
        self.rules_loader.adjust_rule_weight(rule_id, 'negative')
        
        # Get updated weight
        updated_rule = self.rules_loader.get_rule_by_id(rule_id)
        final_weight = updated_rule['weight']
        
        # Check that weight decreased by 10% from updated weight
        expected_final_weight = round(updated_weight * 0.9, 2)
        self.assertEqual(final_weight, expected_final_weight)
    
    def test_add_rule(self):
        """Test adding a new rule"""
        # New rule data
        new_rule = {
            "id": "rule005",
            "emotion": "angry",
            "keyword": "frustrated",
            "action": "suggest_calming",
            "weight": 1.0
        }
        
        # Add the rule
        success = self.rules_loader.add_rule(new_rule)
        
        # Check result
        self.assertTrue(success, "Should successfully add rule")
        
        # Verify rule was added
        added_rule = self.rules_loader.get_rule_by_id('rule005')
        self.assertIsNotNone(added_rule, "Rule should exist after adding")
        self.assertEqual(added_rule['emotion'], 'angry')
        self.assertEqual(added_rule['keyword'], 'frustrated')
    
    def test_update_rule(self):
        """Test updating an existing rule"""
        rule_id = 'rule001'
        
        # Updated data
        updated_data = {
            "keyword": "lonely",
            "weight": 1.8
        }
        
        # Update the rule
        success = self.rules_loader.update_rule(rule_id, updated_data)
        
        # Check result
        self.assertTrue(success, "Should successfully update rule")
        
        # Verify rule was updated
        updated_rule = self.rules_loader.get_rule_by_id(rule_id)
        self.assertEqual(updated_rule['keyword'], 'lonely')
        self.assertEqual(updated_rule['weight'], 1.8)
        
        # Original fields should remain unchanged
        self.assertEqual(updated_rule['emotion'], 'sad')
        self.assertEqual(updated_rule['action'], 'offer_companionship')
    
    def test_delete_rule(self):
        """Test deleting a rule"""
        rule_id = 'rule002'
        
        # Verify rule exists before deletion
        rule_before = self.rules_loader.get_rule_by_id(rule_id)
        self.assertIsNotNone(rule_before, "Rule should exist before deletion")
        
        # Delete the rule
        success = self.rules_loader.delete_rule(rule_id)
        
        # Check result
        self.assertTrue(success, "Should successfully delete rule")
        
        # Verify rule no longer exists
        rule_after = self.rules_loader.get_rule_by_id(rule_id)
        self.assertIsNone(rule_after, "Rule should not exist after deletion")
        
        # Verify rule count decreased
        rules = self.rules_loader.get_rules()
        self.assertEqual(len(rules), 2, "Should have 2 rules after deletion")

if __name__ == '__main__':
    unittest.main()