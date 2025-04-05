"""
Rules Config Loader for Mashaaer Feelings Application
Handles loading, saving, and management of decision rules
"""
import json
import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class RulesConfigLoader:
    """
    Manages the rules configuration for the decision engine
    Supports dynamic weight adjustments based on user feedback
    """
    
    def __init__(self, config_path: str = 'rules_config.json'):
        """Initialize the rules config loader"""
        self.config_path = config_path
        self.rules = self._load_rules()
        logger.info(f"Loaded {len(self.rules)} rules from {config_path}")
    
    def _load_rules(self) -> List[Dict[str, Any]]:
        """Load rules from the configuration file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default rules if file doesn't exist
                default_rules = [
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
                self._save_rules(default_rules)
                return default_rules
        except Exception as e:
            logger.error(f"Error loading rules: {str(e)}")
            return []
    
    def _save_rules(self, rules: List[Dict[str, Any]]) -> bool:
        """Save rules to the configuration file"""
        try:
            # Sort rules by weight in descending order before saving
            sorted_rules = sorted(rules, key=lambda x: x.get('weight', 0), reverse=True)
            
            # Ensure directory exists if there's a directory part in the path
            dirname = os.path.dirname(self.config_path)
            if dirname:  # Only try to create directory if path contains a directory
                os.makedirs(dirname, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(sorted_rules, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(sorted_rules)} rules to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving rules: {str(e)}")
            return False
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """Get all rules sorted by weight"""
        # Return a sorted copy of the rules
        return sorted(self.rules, key=lambda x: x.get('weight', 0), reverse=True)
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific rule by ID"""
        for rule in self.rules:
            if rule.get('id') == rule_id:
                return rule
        return None
    
    def match_rules(self, emotion: str, message: str, language: str = None) -> List[Dict[str, Any]]:
        """
        Match rules based on emotion, keywords, and language in the message
        
        Args:
            emotion: The detected emotion
            message: The user's message
            language: Optional language filter ('en' or 'ar')
            
        Returns:
            Matching rules sorted by weight
        """
        matches = []
        
        # Convert message to lowercase for case-insensitive matching
        message_lower = message.lower()
        
        for rule in self.rules:
            rule_emotion = rule.get('emotion', '').lower()
            rule_keyword = rule.get('keyword', '').lower()
            rule_language = rule.get('lang', 'en').lower()  # Default to English if not specified
            
            # Check language if filter specified
            if language and rule_language != language.lower():
                continue
                
            # Match if emotion matches and keyword is in the message
            if (rule_emotion == emotion.lower() and 
                rule_keyword in message_lower):
                matches.append(rule)
        
        # Sort matches by weight in descending order
        return sorted(matches, key=lambda x: x.get('weight', 0), reverse=True)
    
    def adjust_rule_weight(self, rule_id: str, feedback: str) -> bool:
        """
        Adjust rule weight based on user feedback
        Positive feedback increases weight, negative feedback decreases it
        """
        rule = self.get_rule_by_id(rule_id)
        if not rule:
            logger.warning(f"Rule not found for ID: {rule_id}")
            return False
        
        # Get current weight or default to 1.0
        current_weight = rule.get('weight', 1.0)
        
        # Adjust weight based on feedback type
        if feedback.lower() == 'positive':
            # Increase weight by 10%
            new_weight = current_weight * 1.1
        elif feedback.lower() == 'negative':
            # Decrease weight by 10%
            new_weight = current_weight * 0.9
        else:
            # Invalid feedback type
            logger.warning(f"Invalid feedback type: {feedback}")
            return False
        
        # Update rule weight
        rule['weight'] = round(new_weight, 2)
        logger.info(f"Updated rule {rule_id} weight: {current_weight} -> {rule['weight']}")
        
        # Save updated rules
        return self._save_rules(self.rules)
    
    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """Add a new rule to the configuration"""
        # Validate required fields
        required_fields = ['id', 'emotion', 'keyword', 'action']
        for field in required_fields:
            if field not in rule:
                logger.error(f"Missing required field in rule: {field}")
                return False
        
        # Check if rule with same ID already exists
        existing_rule = self.get_rule_by_id(rule['id'])
        if existing_rule:
            logger.warning(f"Rule with ID {rule['id']} already exists")
            return False
        
        # Ensure weight field exists
        if 'weight' not in rule:
            rule['weight'] = 1.0
        
        # Add rule and save
        self.rules.append(rule)
        return self._save_rules(self.rules)
    
    def update_rule(self, rule_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing rule"""
        rule = self.get_rule_by_id(rule_id)
        if not rule:
            logger.warning(f"Rule not found for ID: {rule_id}")
            return False
        
        # Update rule fields
        for key, value in updated_data.items():
            if key != 'id':  # Don't allow changing the ID
                rule[key] = value
        
        # Save updated rules
        return self._save_rules(self.rules)
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule by ID"""
        rule = self.get_rule_by_id(rule_id)
        if not rule:
            logger.warning(f"Rule not found for ID: {rule_id}")
            return False
        
        # Remove rule and save
        self.rules = [r for r in self.rules if r.get('id') != rule_id]
        return self._save_rules(self.rules)