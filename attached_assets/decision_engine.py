
import datetime
import logging

logger = logging.getLogger(__name__)

class Rule:
    def __init__(self, emotion, keyword, action, params=None, weight=1.0, description=""):
        self.emotion = emotion
        self.keyword = keyword
        self.action = action
        self.params = params or {}
        self.weight = weight
        self.description = description
        self.created_at = datetime.datetime.utcnow()

    def matches(self, message, emotion):
        return self.emotion in (emotion or "") and self.keyword in message.lower()

    def to_dict(self):
        return {
            "emotion": self.emotion,
            "keyword": self.keyword,
            "action": self.action,
            "params": self.params,
            "weight": self.weight,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }

class RobinDecisionEngine:
    def __init__(self):
        self.rules = []
        self.memory = {}

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def decide(self, message, emotion=None):
        matched = [r for r in self.rules if r.matches(message, emotion)]
        if not matched:
            logger.debug("No rule matched. Returning default response.")
            return {"action": "respond_normally", "params": {}}

        matched.sort(key=lambda r: r.weight, reverse=True)
        top_rule = matched[0]
        logger.debug(f"Rule matched: {top_rule.to_dict()}")
        return {"action": top_rule.action, "params": top_rule.params}

    def update_rule_weight(self, rule: Rule, delta):
        rule.weight = max(0, rule.weight + delta)

    def store_memory(self, user_id, data):
        self.memory[user_id] = self.memory.get(user_id, []) + [data]
