# routes/resume_routes.py

from flask import Blueprint, request, jsonify
from utils.jwt_utils import verify_jwt_token
from services.resume_service import analyze_resume

resume_routes = Blueprint("resume_routes", __name__)

@resume_routes.route("/analyze", methods=["POST"])
def analyze():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Missing token"}), 401

    # Verify JWT token
    payload = verify_jwt_token(token)
    if isinstance(payload, str):
        return jsonify({"error": payload}), 401

    user_id = payload["user_id"]
    file = request.files.get("resume")
    job_description = request.form.get("job_description")

    if not file or not job_description:
        return jsonify({"error": "Missing required fields"}), 400

    result = analyze_resume(user_id, file, job_description)
    return jsonify(result), 200
