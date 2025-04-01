import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
import logging

logger = logging.getLogger(__name__)

# Configure Gemini API with error handling
try:
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Gemini configuration failed: {str(e)}")
    raise RuntimeError("AI service initialization failed")

def generate_cover_letter(resume_text, job_description):
    """Generate a professional cover letter with enhanced error handling"""
    try:
        # Validate inputs
        if not isinstance(resume_text, str) or not isinstance(job_description, str):
            raise ValueError("Inputs must be strings")
            
        if len(resume_text) < 50 or len(job_description) < 50:
            raise ValueError("Inputs must be at least 50 characters")

        # Initialize model with safety settings
        model = genai.GenerativeModel(
            'gemini-1.5-pro',
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2048
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
        )

        # Create structured prompt
        prompt = f"""Generate a professional cover letter based on:
        
        Resume:
        {resume_text[:5000]}  # Limit input size
        
        Job Description:
        {job_description[:2000]}  # Limit input size
        
        Requirements:
        - 3-4 well-structured paragraphs
        - Professional and enthusiastic tone
        - Highlight 2-3 key skills from resume that match the job
        - Include specific achievements or experiences
        - Proper business letter format
        - No placeholders - generate complete content
        - Avoid generic phrases
        - Target length: 300-500 words
        """

        # Generate content
        response = model.generate_content(prompt)
        
        if not response.text:
            raise ValueError("Empty response from AI model")

        # Clean and format the response
        cover_letter = clean_cover_letter(response.text)
        
        return cover_letter

    except Exception as e:
        logger.error(f"Cover letter generation failed: {str(e)}")
        return generate_fallback_cover_letter()

def clean_cover_letter(text):
    """Clean and format the generated cover letter"""
    try:
        if not text:
            return generate_fallback_cover_letter()
            
        # Remove markdown code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        
        # Remove any remaining special tokens
        text = re.sub(r'[*_]{2,}', '', text)
        
        # Ensure proper paragraph breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove any incomplete placeholder text
        text = re.sub(r'\[.*?\]', '', text)
        
        return text.strip() or generate_fallback_cover_letter()
        
    except Exception as e:
        logger.error(f"Error cleaning cover letter: {str(e)}")
        return generate_fallback_cover_letter()

def generate_fallback_cover_letter():
    """Generate a generic fallback cover letter"""
    return """Dear Hiring Manager,

I am excited to apply for the position at your company. My skills and experience align well with the requirements of the role.

[Your qualifications and achievements would be highlighted here based on your resume and the job description]

I look forward to the opportunity to discuss how I can contribute to your team. Please feel free to contact me to schedule an interview.

Sincerely,
[Your Name]"""