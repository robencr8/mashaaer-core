import logging
from typing import Dict, Any, Optional

class Rule:
    """
    Rule class for the decision engine.
    Each rule has an emotion trigger, keyword, action, and weight.
    """
    def __init__(self, 
                 emotion: str, 
                 keyword: str, 
                 action: str, 
                 params: Optional[Dict[str, Any]] = None, 
                 weight: float = 1.0,
                 description: str = "",
                 rule_id: str = None,
                 lang: str = "en"):
        self.emotion = emotion
        self.keyword = keyword
        self.action = action
        self.params = params or {}
        self.weight = weight
        self.description = description
        self.id = rule_id
        self.lang = lang
        self.logger = logging.getLogger(__name__)
        
    def matches(self, message: str, emotion: Optional[str] = None) -> bool:
        """
        Check if this rule matches the given message and emotion.
        
        Args:
            message: The user's message
            emotion: The detected emotion (optional)
            
        Returns:
            True if the rule matches, False otherwise
        """
        # Case insensitive keyword matching
        keyword_match = self.keyword.lower() in message.lower()
        
        # If emotion is provided, match it, otherwise just check keyword
        if emotion:
            emotion_match = self.emotion.lower() == emotion.lower()
            match_result = emotion_match and keyword_match
        else:
            match_result = keyword_match
            
        self.logger.debug(f"Rule {self.id or self.action} matching: keyword={keyword_match}, emotion={emotion if emotion else 'None'}, result={match_result}")
        return match_result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary for serialization"""
        result = {
            "emotion": self.emotion,
            "keyword": self.keyword,
            "action": self.action,
            "weight": self.weight,
            "lang": self.lang
        }
        
        if self.params:
            result["params"] = self.params
            
        if self.id:
            result["id"] = self.id
            
        if self.description:
            result["description"] = self.description
            
        return result
        
    def __str__(self) -> str:
        return f"Rule({self.emotion}, {self.keyword}, {self.action}, weight={self.weight})"

class RobinDecisionEngine:
    """
    Decision engine for routing user inputs to appropriate actions
    based on emotion detection and keyword matching.
    """
    def __init__(self):
        self.rules = []
        self.memory = {}
        self.logger = logging.getLogger(__name__)
        
    def add_rule(self, rule: Rule):
        """Add a rule to the engine"""
        self.rules.append(rule)
        self.logger.debug(f"Added rule: {rule}")
        
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID"""
        initial_count = len(self.rules)
        self.rules = [r for r in self.rules if getattr(r, 'id', None) != rule_id]
        return len(self.rules) < initial_count

    def decide(self, message: str, emotion: Optional[str] = None) -> Dict[str, Any]:
        """
        Decide which action to take based on the message and emotion.
        
        Args:
            message: The user's message
            emotion: The detected emotion (optional)
            
        Returns:
            Dict with action and params
        """
        matched = [r for r in self.rules if r.matches(message, emotion)]

        # Add logging to trace decision-making
        self.logger.debug(f"Deciding for message: '{message}' with emotion: {emotion}")
        self.logger.debug(f"Found {len(matched)} matching rules")

        if not matched:
            self.logger.info("No rule matched. Using default response.")
            return {"action": "respond_normally", "params": {}}

        # Sort by weight (highest first)
        matched.sort(key=lambda r: r.weight, reverse=True)
        top_rule = matched[0]

        self.logger.info(f"Matched rule: {top_rule.to_dict()}")
        return {"action": top_rule.action, "params": top_rule.params}
    
    def update_rule_weight(self, rule_id: str, delta: float) -> bool:
        """
        Update a rule's weight based on feedback.
        
        Args:
            rule_id: The ID of the rule to update
            delta: The amount to adjust the weight by
            
        Returns:
            True if the rule was found and updated, False otherwise
        """
        for rule in self.rules:
            if getattr(rule, 'id', None) == rule_id:
                old_weight = rule.weight
                rule.weight = max(0.1, rule.weight + delta)
                self.logger.info(f"Updated rule {rule_id} weight: {old_weight} -> {rule.weight}")
                return True
        return False
    
    def store_memory(self, user_id: str, key: str, value: Any):
        """
        Store a memory for a user.
        
        Args:
            user_id: The user's ID
            key: The memory key
            value: The memory value
        """
        if user_id not in self.memory:
            self.memory[user_id] = {}
        self.memory[user_id][key] = value
        self.logger.debug(f"Stored memory for user {user_id}: {key}={value}")
        
    def get_memory(self, user_id: str, key: str) -> Any:
        """
        Get a memory for a user.
        
        Args:
            user_id: The user's ID
            key: The memory key
            
        Returns:
            The memory value, or None if not found
        """
        return self.memory.get(user_id, {}).get(key)