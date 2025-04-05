import logging

class RobinDecisionEngine:
    def __init__(self):
        self.rules = []
        self.memory = {}
        self.logger = logging.getLogger(__name__)

    def decide(self, message, emotion=None):
        matched = [r for r in self.rules if r.matches(message, emotion)]

        # Add logging to trace decision-making
        self.logger.debug(f"Deciding for message: '{message}' with emotion: {emotion}")

        if not matched:
            return {"action": "respond_normally", "params": {}}

        matched.sort(key=lambda r: r.weight, reverse=True)
        top_rule = matched[0]

        self.logger.info(f"Matched rule: {top_rule.to_dict()}")
        return {"action": top_rule.action, "params": top_rule.params}