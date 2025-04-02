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
        logger.info("Parsing resume file")
        resume_text = parse_resume_file(file)
        if not resume_text:
            raise ValueError("Failed to parse resume file")
        
        logger.debug(f"Resume parsed successfully, length: {len(resume_text)} chars")

        # Analyze with Gemini
        logger.info("Analyzing with Gemini")
        analysis_result = analyze_resume_with_gemini(resume_text, job_description)
        if not analysis_result:
            raise ValueError("Gemini analysis returned no results")
        
        if "error" in analysis_result:
            raise ValueError(f"Gemini error: {analysis_result['error']}")

        logger.debug("Gemini analysis completed successfully")

        # Calculate ATS score
        logger.info("Calculating ATS score")
        ats_score = calculate_ats_score(resume_text, job_description)
        if ats_score is None:
            raise ValueError("Failed to calculate ATS score")
        logger.debug(f"ATS score calculated: {ats_score}")

        # Extract keywords
        logger.info("Extracting keywords")
        resume_keywords = extract_keywords(resume_text) or []
        job_keywords = extract_keywords(job_description) or []
        
        # Format response
        response = {
            "success": True,
            "ats_score": ats_score,
            "keywords": list(set(resume_keywords) & set(job_keywords)),
            "suggestions": analysis_result.get("suggestions", []),
            "missing_keywords": analysis_result.get("missing_keywords", []),
            "score_breakdown": analysis_result.get("score_breakdown", {})
        }

        # Save to database
        logger.info("Saving to database")
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

    except ValueError as ve:
        logger.error(f"Validation error in analyze_resume: {str(ve)}")
        return {"error": str(ve)}
    except Exception as e:
        logger.error(f"Unexpected error in analyze_resume: {str(e)}", exc_info=True)
        return {"error": "Failed to process resume"}
