from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from services.feedback_service import analyze_feedback
from utils.jwt_utils import verify_jwt_token

feedback_routes = Blueprint("feedback_routes", __name__)

@feedback_routes.route("/analyze", methods=["POST"])
@cross_origin()
def analyze():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""

    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    try:
        payload = verify_jwt_token(token)
        if isinstance(payload, str):
            return jsonify({"error": payload}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    data = request.get_json()
    if not data or 'feedback' not in data:
        return jsonify({"error": "Missing feedback"}), 400

    feedback = data['feedback']
    if not feedback or len(feedback.strip()) == 0:
        return jsonify({"error": "Feedback cannot be empty"}), 400

    try:
        result = analyze_feedback(feedback)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "error": f"Analysis failed: {str(e)}",
            "sentiment": "Neutral",
            "sentiment_score": 50,
            "key_insights": ["Unable to generate insights"],
            "improvement_areas": ["Unable to determine improvement areas"],
            "recommendations": "Please try again or provide more detailed feedback."
        }), 500