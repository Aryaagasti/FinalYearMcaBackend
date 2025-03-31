import google.generativeai as genai
import os
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

# Initialize NLP tools
nltk.download('stopwords')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def analyze_resume_with_gemini(resume_text, job_description):
    """
    Enhanced resume analysis using Gemini with structured output and validation
    """
    try:
        # Preprocess texts for better analysis
        cleaned_resume = preprocess_text(resume_text)
        cleaned_jd = preprocess_text(job_description)
        
        # Create structured prompt
        prompt = f"""Analyze this resume against the job description and provide:
        
        Resume:
        {cleaned_resume}
        
        Job Description:
        {cleaned_jd}
        
        Provide output in this exact format:
        
        KEYWORDS: [comma-separated list of matching keywords]
        SUGGESTIONS: [numbered list of specific improvement suggestions]
        SCORE: [percentage match score from 0-100]
        
        Focus on:
        - Technical skills matching
        - Experience relevance
        - Qualifications alignment
        """
        
        # Get response from Gemini
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        
        if not response.text:
            raise ValueError("Empty response from Gemini API")
        
        # Parse the structured response
        return parse_gemini_response(response.text, cleaned_resume, cleaned_jd)
        
    except Exception as e:
        print(f"Gemini analysis error: {str(e)}")
        return {
            "keywords": [],
            "suggestions": ["Failed to analyze with AI. Using fallback method."],
            "match_score": calculate_fallback_score(resume_text, job_description)
        }

def preprocess_text(text):
    """Enhanced text cleaning for analysis"""
    if not text:
        return ""
    
    # Basic cleaning
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # NLP processing
    words = [lemmatizer.lemmatize(w) for w in text.split() if w not in stop_words]
    return ' '.join(words)

def parse_gemini_response(text, resume_text, jd_text):
    """Extract structured data from Gemini response"""
    # Initialize with fallback values
    result = {
        "keywords": [],
        "suggestions": [],
        "match_score": calculate_fallback_score(resume_text, jd_text)
    }
    
    try:
        # Extract keywords
        if "KEYWORDS:" in text:
            kw_line = text.split("KEYWORDS:")[1].split("SUGGESTIONS:")[0].strip()
            result["keywords"] = [kw.strip() for kw in kw_line.split(",") if kw.strip()]
        
        # Extract suggestions
        if "SUGGESTIONS:" in text:
            suggestions_part = text.split("SUGGESTIONS:")[1]
            if "SCORE:" in suggestions_part:
                suggestions_part = suggestions_part.split("SCORE:")[0]
            result["suggestions"] = [
                s.strip() for s in suggestions_part.split("\n") 
                if s.strip() and re.match(r'^\d+\.', s.strip())
            ]
        
        # Extract score
        if "SCORE:" in text:
            score_part = text.split("SCORE:")[1].strip()
            match = re.search(r'\d+', score_part.split("\n")[0])
            if match:
                result["match_score"] = min(100, max(0, int(match.group())))
                
    except Exception as e:
        print(f"Error parsing Gemini response: {str(e)}")
    
    return result

def calculate_fallback_score(resume_text, jd_text):
    """Calculate basic match score if Gemini fails"""
    resume_words = set(preprocess_text(resume_text).split())
    jd_words = set(preprocess_text(jd_text).split())
    common = resume_words & jd_words
    return round((len(common) / max(len(jd_words), 1)) * 100)