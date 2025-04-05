
from flask import Blueprint, jsonify, request
from rule_engine import RobinDecisionEngine, Rule
import logging

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

# Initialize engine with example rules
decision_engine = RobinDecisionEngine()
decision_engine.add_rule(Rule("sad", "alone", "offer_companionship"))
decision_engine.add_rule(Rule("happy", "music", "play_music", {"genre": "uplifting"}))
decision_engine.add_rule(Rule("neutral", "weather", "fetch_weather"))

@api_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '')
    emotion = data.get('emotion', 'neutral')

    result = decision_engine.decide(user_input, emotion)
    action = result["action"]
    params = result.get("params", {})

    logger.info(f"User input: '{user_input}' | Emotion: {emotion} | Action: {action}")

    if action == "fetch_weather":
        return jsonify({"action": "weather", "weather": "Sunny in Ajman 🌞"})

    elif action == "play_music":
        return jsonify({"action": "music", "song": params.get("genre", "uplifting")})

    elif action == "offer_companionship":
        return jsonify({"action": "companion", "reply": "I'm here for you, always 💙"})

    return jsonify({"action": "reply", "reply": "I understand."})

