import os
import re
import json
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

        Respond ONLY with a valid JSON object in the following format:
        {{
            "Overall Sentiment": "Positive/Neutral/Negative",
            "Sentiment Score": 75,
            "Key Insights": ["Insight 1", "Insight 2", "Insight 3"],
            "Improvement Areas": ["Area 1", "Area 2"],
            "Recommendations": "Detailed recommendations text"
        }}

        Ensure the JSON is properly formatted and can be parsed directly."""

        response = model.generate_content(prompt)

        # Try to parse direct JSON response first
        try:
            # Clean the response text to extract just the JSON part
            text = response.text.strip()
            # Find JSON object boundaries
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                data = json.loads(json_str)

                # Map the JSON fields to our expected output format
                return {
                    "sentiment": data.get("Overall Sentiment", "Neutral"),
                    "sentiment_score": int(data.get("Sentiment Score", 50)),
                    "key_insights": data.get("Key Insights", []),
                    "improvement_areas": data.get("Improvement Areas", []),
                    "recommendations": data.get("Recommendations", "")
                }
        except Exception as json_error:
            print(f"JSON parsing failed: {str(json_error)}. Falling back to extraction methods.")

        # Fallback to extraction methods if JSON parsing fails
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

def _extract_sentiment(text):
    """Extract sentiment from Gemini response"""
    try:
        # Try to parse as JSON first
        if '{' in text and '}' in text:
            try:
                # Extract JSON part if it exists
                json_match = re.search(r'({.*})', text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    data = json.loads(json_str)
                    if 'Overall Sentiment' in data:
                        sentiment = data['Overall Sentiment']
                        if isinstance(sentiment, str):
                            if 'positive' in sentiment.lower():
                                return "Positive"
                            elif 'negative' in sentiment.lower():
                                return "Negative"
                            else:
                                return "Neutral"
            except:
                pass

        # Fallback to text parsing
        if re.search(r'sentiment.*?positive', text.lower()) or re.search(r'positive.*?sentiment', text.lower()):
            return "Positive"
        elif re.search(r'sentiment.*?negative', text.lower()) or re.search(r'negative.*?sentiment', text.lower()):
            return "Negative"
        elif re.search(r'sentiment.*?neutral', text.lower()) or re.search(r'neutral.*?sentiment', text.lower()):
            return "Neutral"
    except Exception:
        pass

    # Default fallback
    return "Neutral"

def _calculate_sentiment_score(text):
    """Extract sentiment score from Gemini response"""
    try:
        # Try to parse as JSON first
        if '{' in text and '}' in text:
            try:
                # Extract JSON part if it exists
                json_match = re.search(r'({.*})', text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    data = json.loads(json_str)
                    if 'Sentiment Score' in data:
                        score = data['Sentiment Score']
                        if isinstance(score, (int, float)):
                            return min(100, max(0, int(score)))
                        elif isinstance(score, str) and '%' in score:
                            score_num = int(re.search(r'(\d+)', score).group(1))
                            return min(100, max(0, score_num))
            except:
                pass

        # Fallback to text parsing
        score_match = re.search(r'sentiment score.*?(\d+)', text.lower()) or re.search(r'score.*?(\d+)%', text.lower())
        if score_match:
            return min(100, max(0, int(score_match.group(1))))
    except Exception:
        pass

    # Default based on sentiment
    sentiment = _extract_sentiment(text)
    if sentiment == "Positive":
        return 85
    elif sentiment == "Negative":
        return 25
    else:
        return 50

def _extract_key_insights(text):
    """Extract key insights from Gemini response"""
    try:
        insights = []

        # Try to parse as JSON first
        if '{' in text and '}' in text:
            try:
                # Extract JSON part if it exists
                json_match = re.search(r'({.*})', text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    data = json.loads(json_str)
                    if 'Key Insights' in data:
                        insights_data = data['Key Insights']
                        if isinstance(insights_data, list):
                            return insights_data[:4]  # Limit to 4 insights
                        elif isinstance(insights_data, str):
                            return [insights_data]
            except:
                pass

        # Fallback to text parsing
        insights_section = None

        # Look for insights section
        if 'key insights' in text.lower():
            insights_section = re.split(r'key insights', text, flags=re.IGNORECASE)[1]
            insights_section = insights_section.split('\n\n')[0] if '\n\n' in insights_section else insights_section

        if insights_section:
            # Extract bullet points or numbered items
            items = re.findall(r'(?:^|\n)(?:\d+\.|\*|\-)\s*(.*?)(?:\n|$)', insights_section)
            if items:
                insights = [item.strip() for item in items if item.strip()][:4]  # Limit to 4 insights

        # If we still don't have insights, try to extract sentences
        if not insights and insights_section:
            sentences = re.split(r'(?<=[.!?])\s+', insights_section)
            insights = [s.strip() for s in sentences if len(s.strip()) > 10][:4]  # Limit to 4 insights

        return insights if insights else ["Communication skills", "Technical knowledge", "Professional demeanor"]
    except Exception:
        return ["Communication skills", "Technical knowledge", "Professional demeanor"]

def _extract_improvement_areas(text):
    """Extract improvement areas from Gemini response"""
    try:
        areas = []

        # Try to parse as JSON first
        if '{' in text and '}' in text:
            try:
                # Extract JSON part if it exists
                json_match = re.search(r'({.*})', text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    data = json.loads(json_str)
                    if 'Improvement Areas' in data:
                        areas_data = data['Improvement Areas']
                        if isinstance(areas_data, list):
                            return areas_data[:3]  # Limit to 3 areas
                        elif isinstance(areas_data, str):
                            return [areas_data]
            except:
                pass

        # Fallback to text parsing
        improvement_section = None

        # Look for improvement section with various possible headings
        for heading in ['improvement areas', 'areas for improvement', 'improvement suggestions']:
            if heading in text.lower():
                improvement_section = re.split(heading, text, flags=re.IGNORECASE)[1]
                improvement_section = improvement_section.split('\n\n')[0] if '\n\n' in improvement_section else improvement_section
                break

        if improvement_section:
            # Extract bullet points or numbered items
            items = re.findall(r'(?:^|\n)(?:\d+\.|\*|\-)\s*(.*?)(?:\n|$)', improvement_section)
            if items:
                areas = [item.strip() for item in items if item.strip()][:3]  # Limit to 3 areas

        # If we still don't have areas, try to extract sentences
        if not areas and improvement_section:
            sentences = re.split(r'(?<=[.!?])\s+', improvement_section)
            areas = [s.strip() for s in sentences if len(s.strip()) > 10][:3]  # Limit to 3 areas

        return areas if areas else ["Technical skills", "Communication clarity", "Professional development"]
    except Exception:
        return ["Technical skills", "Communication clarity", "Professional development"]

def _extract_recommendations(text):
    """Extract recommendations from Gemini response"""
    try:
        # Try to parse as JSON first
        if '{' in text and '}' in text:
            try:
                # Extract JSON part if it exists
                json_match = re.search(r'({.*})', text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    data = json.loads(json_str)
                    if 'Recommendations' in data:
                        recs = data['Recommendations']
                        if isinstance(recs, list):
                            return ". ".join(recs)
                        elif isinstance(recs, str):
                            return recs
            except:
                pass

        # Fallback to text parsing
        recommendations_section = None

        # Look for recommendations section with various possible headings
        for heading in ['recommendations', 'actionable recommendations', 'professional recommendations']:
            if heading in text.lower():
                recommendations_section = re.split(heading, text, flags=re.IGNORECASE)[1]
                recommendations_section = recommendations_section.split('\n\n')[0] if '\n\n' in recommendations_section else recommendations_section
                break

        if recommendations_section:
            # Clean up the recommendations text
            recommendations = recommendations_section.strip()
            # Remove bullet points or numbers
            recommendations = re.sub(r'(?:^|\n)(?:\d+\.|\*|\-)\s*', ' ', recommendations)
            # Clean up extra whitespace
            recommendations = re.sub(r'\s+', ' ', recommendations).strip()

            if len(recommendations) > 10:
                return recommendations

        # Default recommendation based on sentiment
        sentiment = _extract_sentiment(text)
        if sentiment == "Positive":
            return "Continue building on strengths while addressing minor improvement areas for professional growth."
        elif sentiment == "Negative":
            return "Focus on addressing key improvement areas through targeted skill development and seeking mentorship."
        else:
            return "Balance maintaining current strengths with developing specific skills to enhance overall professional performance."
    except Exception:
        return "Focus on developing technical expertise, enhance presentation skills, and improve collaborative communication."
