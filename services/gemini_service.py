import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API with your key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_resume_with_gemini(resume_text, job_description):
    try:
        # ✅ Use the correct model name
        model = genai.GenerativeModel("gemini-2.0-flash")  # or 'models/gemini-1.5-flash' for a faster version

        # Create a structured prompt
        prompt = (
            f"Analyze this resume:\n{resume_text}\n\n"
            f"For this job description:\n{job_description}\n\n"
            f"1. Suggest keywords\n"
            f"2. Provide improvements\n"
        )

        # ✅ Generate content using Gemini API
        response = model.generate_content(prompt)

        if not response or not response.text:
            return {"error": "No response from Gemini API"}

        # ✅ Extract keywords and suggestions
        response_lines = response.text.strip().split("\n")
        keywords = response_lines[0] if len(response_lines) > 0 else "No keywords found"
        suggestions = response_lines[1:] if len(response_lines) > 1 else ["No suggestions provided"]

        # ✅ Calculate Match Score
        resume_keywords = set(resume_text.lower().split())
        job_keywords = set(job_description.lower().split())
        matched_keywords = resume_keywords.intersection(job_keywords)
        match_score = round((len(matched_keywords) / max(len(job_keywords), 1)) * 100)  # Avoid division by zero

        return {
            "match_score": match_score,
            "keywords": keywords,
            "suggestions": suggestions
        }

    except Exception as e:
        return {"error": str(e)}

