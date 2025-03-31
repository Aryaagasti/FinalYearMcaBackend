from flask import Blueprint, request, jsonify
from services.cover_letter_service import generate_cover_letter
from utils.jwt_utils import verify_jwt_token

cover_letter_routes = Blueprint("cover_letter_routes", __name__)

@cover_letter_routes.route("/generate", methods=["POST"])
def generate():
    # Validate the request
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    # Verify JWT token
    payload = verify_jwt_token(token)
    if isinstance(payload, str):
        return jsonify({"error": payload}), 401

    # Extract data from the request
    resume_text = request.json.get("resume_text")
    job_description = request.json.get("job_description")

    if not resume_text or not job_description:
        return jsonify({"error": "Missing required fields"}), 400

    # Generate the cover letter
    try:
        cover_letter = generate_cover_letter(resume_text, job_description)
        return jsonify({"cover_letter": cover_letter}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500