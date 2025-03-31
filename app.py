# app.py

from flask import Flask, render_template
from flask_cors import CORS
from routes.auth_routes import auth_routes
from routes.resume_routes import resume_routes
from routes.job_routes import job_routes
from routes.feedback_routes import feedback_routes
from routes.course_routes import course_routes
from routes.user_routes import user_routes
from routes.cover_letter_routes import cover_letter_routes
from config.db import init_db
import os

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 600  # Cache preflight response for 10 minutes
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response


# Initialize MongoDB with app
mongo = init_db(app)

# Register routes
app.register_blueprint(auth_routes, url_prefix="/api/auth")
app.register_blueprint(resume_routes, url_prefix="/api/resume")
app.register_blueprint(job_routes, url_prefix="/api/job")
app.register_blueprint(feedback_routes, url_prefix="/api/feedback")
app.register_blueprint(course_routes, url_prefix="/api/course")
app.register_blueprint(user_routes, url_prefix="/api/user")
app.register_blueprint(cover_letter_routes, url_prefix="/api/cover-letter")



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get Render's assigned port
    app.run(host="0.0.0.0", port=port, debug=True)
