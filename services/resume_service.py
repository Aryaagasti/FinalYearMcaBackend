from models.resume_model import Resume
from services.ats_score_service import calculate_ats_score
from services.gemini_service import analyze_resume_with_gemini
from utils.file_parser import parse_resume_file
from utils.keyword_extractor import extract_keywords
import logging

logger = logging.getLogger(__name__)

def analyze_resume(user_id, file, job_description):
    try:
        logger.info(f"Starting resume analysis for user {user_id}")

        # Validate file
        if not file or file.filename == '':
            raise ValueError("No resume file provided")

        # Parse the resume file
        resume_text = parse_resume_file(file)
        if not resume_text:
            raise ValueError("Failed to parse resume file")
        
        logger.debug(f"Resume parsed successfully, length: {len(resume_text)} chars")

        # Analyze with Gemini
        analysis_result = analyze_resume_with_gemini(resume_text, job_description)
        if not analysis_result:
            raise ValueError("Gemini analysis failed")
        
        logger.debug("Gemini analysis completed")

        # Calculate ATS score
        ats_score = calculate_ats_score(resume_text, job_description)
        logger.debug(f"ATS score calculated: {ats_score}")

        # Extract keywords
        resume_keywords = extract_keywords(resume_text) or []
        job_keywords = extract_keywords(job_description) or []
        
        # Format response
        response = {
            "ats_score": ats_score,
            "keywords": list(set(resume_keywords) & set(job_keywords)),
            "suggestions": analysis_result.get("suggestions", []),
            "missing_keywords": analysis_result.get("missing_keywords", []),
            "score_breakdown": analysis_result.get("score_breakdown", {})
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
        logger.info("Resume data saved to database")

        return response

    except Exception as e:
        logger.error(f"Error in analyze_resume: {str(e)}")
        return {"error": str(e)}