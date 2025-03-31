from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from io import BytesIO
from services.job_matching_service import fetch_jobs
from services.resume_service import analyze_resume

job_routes = Blueprint('job_routes', __name__)

@job_routes.route('/match', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def match_jobs():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        return response, 200
        
    try:
        # Check authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing authorization token'}), 401
            
        # Validate file upload
        if 'resume' not in request.files:
            return jsonify({'error': 'Resume file is required'}), 400
            
        resume_file = request.files['resume']
        query = request.form.get('query', 'Software Engineer')
        location = request.form.get('location', 'India')

        # Process the file
        file_content = BytesIO(resume_file.read())
        file_content.filename = resume_file.filename

        # Fetch and analyze jobs
        jobs = fetch_jobs(query, location)
        matched_jobs = []

        for job in jobs:
            match_result = analyze_resume(None, file_content, job.get('description', ''))
            
            matched_jobs.append({
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "location": job.get("location", ""),
                "matching_score": match_result.get("matching_score", 0),
                "matched_skills": match_result.get("matched_skills", []),
                "missing_skills": match_result.get("missing_skills", []),
                "recommendation": match_result.get("recommendation", ""),
                "url": job.get("related_links", [{}])[0].get("link", "") if job.get("related_links") else ""
            })

        response = jsonify({"success": True, "jobs": matched_jobs})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500