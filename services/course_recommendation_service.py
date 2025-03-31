import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def recommend_courses(resume_text):
    try:
        # Use Gemini Pro model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Detailed prompt for structured course recommendations
        prompt = f"""
        Analyze the following resume and recommend 3-4 online courses or certifications 
        that can help improve the candidate's skills and career prospects:

        Resume: {resume_text}

        Please provide recommendations in the following JSON format:
        {{
            "courses": [
                {{
                    "title": "Course Title",
                    "platform": "Course Platform",
                    "description": "Brief course description",
                    "skill_category": "Relevant Skill Category",
                    "duration": "Course Duration",
                    "url": "Course URL"
                }}
            ]
        }}

        Ensure the recommendations are tailored to the skills and experience in the resume.
        """
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        courses = parse_course_recommendations(response.text)
        
        return {
            "success": True,
            "courses": courses
        }
    
    except Exception as e:
        print(f"Error in course recommendation: {e}")
        return {
            "success": False,
            "error": str(e),
            "courses": get_default_courses()
        }

def parse_course_recommendations(text):
    # Try to extract JSON from the response
    try:
        # Remove any text before and after JSON
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            parsed_data = json.loads(json_text)
            
            # Validate the parsed courses
            if parsed_data.get('courses'):
                return parsed_data['courses']
    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON parsing error: {e}")
    
    # Fallback to default courses if parsing fails
    return get_default_courses()

def get_default_courses():
    """
    Provide default course recommendations if parsing fails
    """
    return [
        {
            "title": "Professional Skills Enhancement",
            "platform": "Coursera",
            "description": "A comprehensive course to improve professional skills",
            "skill_category": "Professional Development",
            "duration": "3-4 months",
            "url": "https://www.coursera.org/professional-skills"
        },
        {
            "title": "Technical Skills Masterclass",
            "platform": "Udemy",
            "description": "Advanced technical skills for modern professionals",
            "skill_category": "Technical Skills",
            "duration": "2-3 months",
            "url": "https://www.udemy.com/technical-skills"
        }
    ]