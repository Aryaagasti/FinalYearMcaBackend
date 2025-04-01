from flask import Blueprint, request, jsonify
from utils.jwt_utils import verify_jwt_token
from services.resume_service import analyze_resume
import logging

resume_routes = Blueprint("resume_routes", __name__)
logger = logging.getLogger(__name__)

@resume_routes.route("/analyze", methods=["POST"])
def analyze():
    try:
        # Verify JWT token
        token = request.headers.get("Authorization")
        if not token:
            logger.error("Missing authorization token")
            return jsonify({"error": "Authorization token required"}), 401

        payload = verify_jwt_token(token)
        if isinstance(payload, str):
            logger.error(f"Token verification failed: {payload}")
            return jsonify({"error": payload}), 401

        # Get files and data
        if 'resume' not in request.files:
            logger.error("No resume file uploaded")
            return jsonify({"error": "Resume file is required"}), 400

        file = request.files['resume']
        job_description = request.form.get('job_description', '').strip()

        if not job_description:
            logger.error("Empty job description")
            return jsonify({"error": "Job description is required"}), 400

        # Process the resume
        result = analyze_resume(payload["user_id"], file, job_description)
        
        if "error" in result:
            logger.error(f"Analysis error: {result['error']}")
            return jsonify(result), 400
            
        logger.info("Resume analysis completed successfully")
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500