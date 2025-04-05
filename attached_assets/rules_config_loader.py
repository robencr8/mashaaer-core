import json
from rule_engine import Rule, RobinDecisionEngine
import logging

logger = logging.getLogger(__name__)

def load_rules_from_config(filepath='rules_config.json'):
    engine = RobinDecisionEngine()

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
    except FileNotFoundError:
        logger.warning(f"Rules config file not found: {filepath}")
        return engine
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in rules config: {e}")
        return engine

    for entry in rules_data:
        rule = Rule(
            emotion=entry.get('emotion'),
            keyword=entry.get('keyword'),
            action=entry.get('action'),
            params=entry.get('params', {}),
            weight=entry.get('weight', 1.0),
            description=entry.get('description', '')
        )
        engine.add_rule(rule)
        logger.info(f"Loaded rule: {rule.to_dict()}")

    return engine
