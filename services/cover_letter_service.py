import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_cover_letter(resume_text, job_description):
    try:
        # Use Gemini Pro model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Simplified prompt for cover letter generation
        prompt = f"""
        Generate a professional cover letter based on the following:

        Resume:
        {resume_text}

        Job Description:
        {job_description}

        Guidelines:
        - Highlight 2-3 key skills from the resume that match the job description
        - Create a compelling narrative that connects the candidate's experience to the role
        - Use a professional and enthusiastic tone
        - Include:
          1. Strong opening paragraph
          2. 1-2 paragraphs showcasing relevant skills and achievements
          3. Closing paragraph expressing interest

        Format the cover letter in a clear, readable format.
        """
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Clean and format the response
        cover_letter = clean_cover_letter(response.text)
        
        return cover_letter
    
    except Exception as e:
        print(f"Cover letter generation error: {e}")
        return generate_fallback_cover_letter(resume_text, job_description)

def clean_cover_letter(text):
    """
    Clean and format the generated cover letter
    """
    # Remove any leading/trailing whitespace
    text = text.strip()
    
    # Remove any potential JSON or code block markers
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'\{.*?\}', '', text, flags=re.DOTALL)
    
    # Ensure proper formatting
    if not text:
        return generate_fallback_cover_letter()
    
    return text

def generate_fallback_cover_letter(resume_text="", job_description=""):
    """
    Generate a generic cover letter if AI generation fails
    """
    return f"""
Dear Hiring Manager,

I am writing to express my strong interest in the position outlined in the job description. 
After carefully reviewing the requirements, I believe my skills and experience make me an 
excellent candidate for this role.

My background has equipped me with relevant skills that align with the job's requirements. 
I am confident in my ability to contribute effectively to your team and organization.

Thank you for considering my application. I look forward to the opportunity to discuss 
how my background can benefit your team.

Sincerely,
[Your Name]
"""