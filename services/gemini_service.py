import os
import re
import nltk
import google.generativeai as genai
from dotenv import load_dotenv
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# 🔐 Load .env variables
load_dotenv()

# 📡 Get API key from env
genai_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=genai_api_key)

# 🔤 Download NLTK resources
nltk.download('stopwords')
nltk.download('wordnet')

# ⚙️ NLP setup
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = [lemmatizer.lemmatize(w) for w in text.split() if w not in stop_words]
    return ' '.join(words)

def calculate_fallback_score(resume_text, jd_text):
    resume_words = set(preprocess_text(resume_text).split())
    jd_words = set(preprocess_text(jd_text).split())
    common = resume_words & jd_words
    return round((len(common) / max(len(jd_words), 1)) * 100)

def parse_gemini_response(text, resume_text, jd_text):
    result = {
        "keywords": [],
        "suggestions": [],
        "match_score": calculate_fallback_score(resume_text, jd_text)
    }
    try:
        if "KEYWORDS:" in text:
            kw_line = text.split("KEYWORDS:")[1].split("SUGGESTIONS:")[0].strip()
            result["keywords"] = [kw.strip() for kw in kw_line.split(",") if kw.strip()]
        if "SUGGESTIONS:" in text:
            suggestions_part = text.split("SUGGESTIONS:")[1].split("SCORE:")[0]
            result["suggestions"] = [
                s.strip() for s in suggestions_part.split("\n")
                if s.strip() and re.match(r'^\d+\.', s.strip())
            ]
        if "SCORE:" in text:
            score_part = text.split("SCORE:")[1].strip()
            match = re.search(r'\d+', score_part.split("\n")[0])
            if match:
                result["match_score"] = min(100, max(0, int(match.group())))
    except Exception as e:
        print(f"Parsing error: {e}")
    return result

def analyze_resume_with_gemini(resume_text, job_description):
    try:
        cleaned_resume = preprocess_text(resume_text)
        cleaned_jd = preprocess_text(job_description)

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

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        if not hasattr(response, 'text') or not response.text:
            raise ValueError("Empty or invalid response from Gemini API")

        print("Gemini raw response:", response.text)
        return parse_gemini_response(response.text, cleaned_resume, cleaned_jd)

    except Exception as e:
        print(f"Gemini analysis error: {str(e)}")
        return {
            "keywords": [],
            "suggestions": ["Failed to analyze with AI. Using fallback method."],
            "match_score": calculate_fallback_score(resume_text, job_description)
        }

# 🧪 Example usage
if __name__ == "__main__":
    resume_sample = "Experienced software developer skilled in Python, Django, REST APIs."
    job_desc_sample = "Looking for a Python developer with Django, Flask, and API experience."
    result = analyze_resume_with_gemini(resume_sample, job_desc_sample)
    print("\nFinal Result:\n", result)
