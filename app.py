from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_routes
from routes.resume_routes import resume_routes

from routes.feedback_routes import feedback_routes
from routes.course_routes import course_routes
from routes.user_routes import user_routes
from routes.chatbot_routes import chatbot_routes
from routes.cover_letter_routes import cover_letter_routes
from config.db import init_db
import os

app = Flask(__name__)

# Correct CORS configuration
CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://resumepro-resume-analyzer-career.onrender.com"
]}})

# Ensure no conflicting CORS headers
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

# Initialize MongoDB
mongo = init_db(app)

# Register all blueprints
app.register_blueprint(auth_routes, url_prefix="/api/auth")
app.register_blueprint(resume_routes, url_prefix="/api/resume")
app.register_blueprint(feedback_routes, url_prefix="/api/feedback")
app.register_blueprint(course_routes, url_prefix="/api/course")
app.register_blueprint(user_routes, url_prefix="/api/user")
app.register_blueprint(chatbot_routes, url_prefix="/api/chatbot")
app.register_blueprint(cover_letter_routes, url_prefix="/api/cover-letter")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
