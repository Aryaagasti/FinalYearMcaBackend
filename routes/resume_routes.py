from flask import Blueprint, request, jsonify
from utils.jwt_utils import verify_jwt_token
from services.resume_service import analyze_resume
import logging

resume_routes = Blueprint("resume_routes", __name__)
logger = logging.getLogger(__name__)

@resume_routes.route("/analyze", methods=["POST"])
def analyze():
    try:
        logger.info("Starting resume analysis request")

        # Verify JWT token
        token = request.headers.get("Authorization")
        if not token:
            logger.error("Missing authorization token")
            return jsonify({"error": "Authorization token required"}), 401

        logger.info(f"Received Authorization header: {token[:20]}...")  # Partial log for debugging
        payload = verify_jwt_token(token)

        if isinstance(payload, dict) and "error" in payload:
            logger.error(f"Token verification failed: {payload['error']}")
            return jsonify({"error": payload["error"]}), 401

        user_id = payload.get("user_id")
        if not user_id:
            logger.error("Invalid token payload, missing user_id")
            return jsonify({"error": "Invalid token payload"}), 401

        logger.info(f"Token verified for user {user_id}")

        # Validate file and job description
        if 'resume' not in request.files:
            logger.error("No resume file uploaded")
            return jsonify({"error": "Resume file is required"}), 400

        file = request.files['resume']
        job_description = request.form.get('job_description', '').strip()

        if not job_description:
            logger.error("Empty job description")
            return jsonify({"error": "Job description is required"}), 400

        # Process the resume
        logger.info(f"Processing resume for user {user_id}")
        result = analyze_resume(user_id, file, job_description)

        if "error" in result:
            logger.error(f"Analysis error: {result['error']}")
            return jsonify(result), 400

        logger.info("Resume analysis completed successfully")
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
