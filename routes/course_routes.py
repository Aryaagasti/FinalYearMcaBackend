from flask import Blueprint, request, jsonify
from services.course_recommendation_service import recommend_courses
from utils.jwt_utils import verify_jwt_token

course_routes = Blueprint("course_routes", __name__)

@course_routes.route("/recommend", methods=["POST"])
def recommend():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    # Verify JWT token
    payload = verify_jwt_token(token)
    if isinstance(payload, str):
        return jsonify({"error": payload}), 401

    resume_text = request.json.get("resume_text")
    if not resume_text:
        return jsonify({"error": "Missing resume text"}), 400

    result = recommend_courses(resume_text)
    return jsonify(result), 200