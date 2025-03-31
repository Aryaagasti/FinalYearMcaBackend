import requests
import google.generativeai as genai
import os
import json
import time
from dotenv import load_dotenv
from io import BytesIO
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from models.resume_model import Resume
from services.ats_score_service import calculate_ats_score
from utils.file_parser import parse_resume_file
from utils.keyword_extractor import extract_keywords

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# SerpAPI configuration
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def fetch_jobs(query, location="India"):
    """ Fetch job listings using SerpAPI. """
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_jobs",
            "q": query,
            "location": location,
            "api_key": SERPAPI_API_KEY,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("jobs_results", [])
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []

def analyze_resume_with_gemini(resume_text, job_description):
    """Analyze resume against job description using Gemini API."""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        Analyze this resume: {resume_text}
        Against this job description: {job_description}
        Provide the following in JSON format:
        {{
            "matching_score": 0-100,
            "matched_skills": ["skill1", "skill2"],
            "missing_skills": ["skill3", "skill4"],
            "recommendation": "Your recommendation here"
        }}
        """
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        print(f"Time taken for Gemini API call: {end_time - start_time:.2f} seconds")
        
        # Check if the response is valid
        if not response.text:
            raise ValueError("Empty response from Gemini API")
        
        # Safely parse JSON response
        result = json.loads(response.text)
        print(f"Gemini API response: {result}")
        return result
    except Exception as e:
        print(f"Error analyzing resume with Gemini: {e}")
        return {
            "matching_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "recommendation": "Unable to analyze resume."
        }

def analyze_resume(user_id, file, job_description):
    try:
        # Parse the resume file (PDF/DOCX)
        resume_text = parse_resume_file(file)
        if not resume_text:
            print("Error: Failed to parse resume file")
            return {"error": "Failed to parse resume file"}, 400
        
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
            "suggestions": analysis_result.get("suggestions", []),  # Ensure suggestions is an array
            "matched_skills": analysis_result.get("matched_skills", []),
            "missing_skills": analysis_result.get("missing_skills", []),
            "recommendation": analysis_result.get("recommendation", "")
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