import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_feedback(feedback):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""Analyze the following professional feedback comprehensively:
        {feedback}

        Provide a detailed analysis including:
        1. Overall Sentiment (Positive/Neutral/Negative)
        2. Precise Sentiment Score (0-100%)
        3. 3-4 Specific Key Insights
        4. 2-3 Concrete Improvement Areas
        5. Actionable Professional Recommendations

        Respond in a structured JSON format that can be directly parsed."""

        response = model.generate_content(prompt)
        
        # Example structured response parsing
        return {
            "sentiment": _extract_sentiment(response.text),
            "sentiment_score": _calculate_sentiment_score(response.text),
            "key_insights": _extract_key_insights(response.text),
            "improvement_areas": _extract_improvement_areas(response.text),
            "recommendations": _extract_recommendations(response.text)
        }
    
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "sentiment": "Neutral",
            "sentiment_score": 50,
            "key_insights": ["Unable to generate insights"],
            "improvement_areas": ["Unable to determine improvement areas"],
            "recommendations": "Please try again or provide more detailed feedback."
        }

# Placeholder extraction functions (replace with actual logic)
def _extract_sentiment(text):
    if "Positive" in text: return "Positive"
    if "Negative" in text: return "Negative"
    return "Neutral"

def _calculate_sentiment_score(text):
    return 75  # Placeholder

def _extract_key_insights(text):
    return ["Professional communication", "Performance potential", "Areas of expertise"]

def _extract_improvement_areas(text):
    return ["Technical skills", "Presentation abilities", "Collaborative approach"]

def _extract_recommendations(text):
    return "Focus on developing technical expertise, enhance presentation skills, and improve collaborative communication."