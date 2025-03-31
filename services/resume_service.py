# services/resume_service.py
from models.resume_model import Resume
from services.ats_score_service import calculate_ats_score
from services.gemini_service import analyze_resume_with_gemini
from utils.file_parser import parse_resume_file
from utils.keyword_extractor import extract_keywords

def analyze_resume(user_id, file, job_description):
    try:
        # Parse the resume file (PDF/DOCX)
        resume_text = parse_resume_file(file)
        print(f"Parsed resume text: {resume_text[:100]}...")  # Print first 100 characters of resume text
        
        # Analyze the resume using the Gemini API
        analysis_result = analyze_resume_with_gemini(resume_text, job_description)
        print(f"Analysis result: {analysis_result}")
        
        # Calculate the ATS score
        ats_score = calculate_ats_score(resume_text, job_description)
        print(f"Calculated ATS score: {ats_score}")
        
        # Extract keywords from the resume and job description
        resume_keywords = extract_keywords(resume_text)
        job_keywords = extract_keywords(job_description)
        
        # Format the response
        response = {
            "ats_score": ats_score,
            "keywords": list(set(resume_keywords) & set(job_keywords)),  # Intersection of resume and job keywords
            "suggestions": analysis_result.get("suggestions", [])  # Ensure suggestions is an array
        }
        
        # Save the resume data to MongoDB
        resume = Resume(
            user_id=user_id,
            resume_text=resume_text,
            ats_score=ats_score,
            keywords=response["keywords"],
            suggestions=response["suggestions"]
        )
        resume.save()
        
        # Return the analysis results
        return response
    except Exception as e:
        print(f"Error analyzing resume: {str(e)}")
        return {"error": str(e)}, 500
