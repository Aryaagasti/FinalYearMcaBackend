from flask import Blueprint, request, jsonify
import google.generativeai as genai
from config.db import init_db
from utils.jwt_utils import verify_jwt_token
import os

chatbot_routes = Blueprint("chatbot_routes", __name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@chatbot_routes.route("/ask", methods=["POST"])
def ask_question():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(" ")[1]
    verification = verify_jwt_token(token)
    
    if isinstance(verification, dict) and "error" in verification:
        return jsonify({"error": verification["error"]}), 401
    
    data = request.get_json()
    question = data.get("question")
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    try:
        # Create a friendly prompt
        prompt = f"""
        Act as a friendly career advisor (like an elder sibling). The user is asking: {question}
        
        Respond with:
        1. Helpful career advice in simple language
        2. If resume-related, include ATS score tips
        3. Relevant free YouTube playlist links
        4. Motivational support
        
        Format your response with clear sections using markdown.
        """
        
        response = model.generate_content(prompt)
        return jsonify({"answer": response.text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chatbot_routes.route("/resources", methods=["GET"])
def get_resources():
    # Predefined career resources
    resources = {
        "dsa": "https://youtube.com/playlist?list=PL9gnSGHSqcnr_DxHsP7AW9ftq0AtAyYqJ",
        "web_dev": "https://youtube.com/playlist?list=PLfqMhTWNBTe3H6c9OGXb5_6wcc1Mca52n",
        "resume_tips": "https://youtube.com/playlist?list=PLOGE4peqBpeuIW1V7KkQ3HqfJ6jQjUQwS",
        "interview_prep": "https://youtube.com/playlist?list=PLDzeHZWIZsTrhXYYtx4z8-u8zA-DzuVsj",
        "career_guidance": "https://youtube.com/playlist?list=PL-Jc9J83PIiFj7YSPl2ulcpwy-mwj1SSk"
    }
    return jsonify(resources), 200