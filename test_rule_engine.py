
import unittest
from rule_engine import RobinDecisionEngine, Rule

class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        self.decision_engine = RobinDecisionEngine()
        self.decision_engine.add_rule(Rule("sad", "alone", "offer_companionship"))
        self.decision_engine.add_rule(Rule("happy", "music", "play_music", {"genre": "uplifting"}))
        self.decision_engine.add_rule(Rule("neutral", "weather", "fetch_weather"))

    def test_rule_matching_sad(self):
        result = self.decision_engine.decide("I feel alone", "sad")
        self.assertEqual(result["action"], "offer_companionship")

    def test_rule_matching_happy(self):
        result = self.decision_engine.decide("I like music", "happy")
        self.assertEqual(result["action"], "play_music")

    def test_weight_adjustment(self):
        # Example: Add logic to test weight adjustments
        pass

if __name__ == '__main__':
    unittest.main()
