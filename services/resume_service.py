from flask import Blueprint, request, jsonify
from models.resume_model import Resume
from services.ats_score_service import calculate_ats_score
from services.gemini_service import analyze_resume_with_gemini
from utils.file_parser import parse_resume_file
from utils.keyword_extractor import extract_keywords
import logging
import uuid

resume_routes = Blueprint("resume_routes", __name__)
logger = logging.getLogger(__name__)

@resume_routes.route("/analyze", methods=["POST"])
def analyze_resume_endpoint():
    try:
        # Get request data
        file = request.files.get('resume')
        job_description = request.form.get('job_description', '').strip()
        
        # Validate input
        if not file or file.filename == '':
            return jsonify({"success": False, "error": "No resume file provided"}), 400
            
        if not job_description:
            return jsonify({"success": False, "error": "Job description is required"}), 400

        # Process the resume (using a mock user_id for this example)
        result = analyze_resume("mock_user_id", file, job_description)
        
        if "error" in result:
            return jsonify({"success": False, "error": result["error"]}), 400

        # Format the response exactly as specified
        response = {
            "success": True,
            "resumeId": "67ee32a47c1314b345e2b450",  # Using a mock ID
            "atsScore": result["ats_score"],
            "keywords": result["keywords"],
            "suggestions": result["suggestions"],
            "missingKeywords": result["missing_keywords"],
            "scoreBreakdown": result["score_breakdown"]
        }
        
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "Internal server error"}), 500


def analyze_resume(user_id, file, job_description):
    try:
        logger.info(f"Starting resume analysis for user {user_id}")

        # Parse the resume file
        resume_text = parse_resume_file(file)
        if not resume_text:
            raise ValueError("Failed to parse resume file")
        
        # Analyze with Gemini
        analysis_result = analyze_resume_with_gemini(resume_text, job_description)
        if not analysis_result or "error" in analysis_result:
            raise ValueError(analysis_result.get("error", "Gemini analysis failed"))

        # Calculate ATS score
        ats_score = calculate_ats_score(resume_text, job_description)
        if ats_score is None:
            raise ValueError("Failed to calculate ATS score")

        # Extract keywords
        resume_keywords = extract_keywords(resume_text) or []
        job_keywords = extract_keywords(job_description) or []
        
        # Format response with all required fields
        response = {
            "success": True,
            "ats_score": ats_score,
            "keywords": list(set(resume_keywords) & set(job_keywords)),
            "suggestions": analysis_result.get("suggestions", []),
            "missing_keywords": list(set(job_keywords) - set(resume_keywords)),
            "score_breakdown": {
                "keywords": analysis_result.get("match_score", 0),
                "experience": analysis_result.get("experience_score", 20),
                "education": analysis_result.get("education_score", 75),
                "formatting": analysis_result.get("formatting_score", 90)
            }
        }

        # Save to database
        resume = Resume(
            user_id=user_id,
            resume_text=resume_text,
            ats_score=ats_score,
            keywords=response["keywords"],
            suggestions=response["suggestions"]
        )
        resume.save()

        return response

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return {"error": str(ve)}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"error": "Failed to process resume"}
