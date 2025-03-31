from flask import Blueprint, request, jsonify
from io import BytesIO
from services.resume_service import analyze_resume
from services.job_matching_service import fetch_jobs
from models.job_matching_model import JobMatchingResponse

# Create a Blueprint for job routes
job_routes = Blueprint('job_routes', __name__)

@job_routes.route('/job', methods=['POST'])
@job_routes.route('/job', methods=['POST'])
def match_jobs():
    """ Endpoint to match a resume with job listings. """
    try:
        # Validate resume file upload
        if 'resume' not in request.files:
            return jsonify({'error': 'Resume file is required'}), 400
        
        resume_file = request.files['resume']
        query = request.form.get('query', 'Software Engineer')
        location = request.form.get('location', 'India')

        # Use BytesIO to read file content
        file_content = BytesIO(resume_file.read())
        file_content.filename = resume_file.filename

        # Fetch jobs and analyze resume
        jobs = fetch_jobs(query, location)
        matched_jobs = []

        for job in jobs:
            match_result = analyze_resume(None, file_content, job.get('description', ''))
            
            # Log the match result
            print("Match Result:", match_result)
            
            # Create a JobMatchingResponse object
            job_response = {
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "location": job.get("location", ""),
                "matching_score": match_result.get("matching_score", 0),
                "matched_skills": match_result.get("matched_skills", []),
                "missing_skills": match_result.get("missing_skills", []),
                "recommendation": match_result.get("recommendation", ""),
                "url": job.get("related_links", [{}])[0].get("link", "") if job.get("related_links") else ""
            }
            
            matched_jobs.append(job_response)

        # Log the final response
        print("Final Response:", {"success": True, "jobs": matched_jobs})
        
        return jsonify({"success": True, "jobs": matched_jobs}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500