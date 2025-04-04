from flask import Blueprint, request, jsonify
from models.user_model import User
from utils.jwt_utils import verify_jwt_token
from models.resume_model import Resume
from bson import ObjectId
from config.db import get_db

user_routes = Blueprint("user_routes", __name__)

# Fetch user profile details
@user_routes.route("/profile", methods=["GET"])
def get_user_profile():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Token is missing"}), 401

    # Verify JWT token
    payload = verify_jwt_token(token)
    if isinstance(payload, str):  # If payload is a string, it's an error message
        return jsonify({"error": payload}), 401

    user_id = payload.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 400

    # Fetch the user from the database
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch user's resumes
    resumes = Resume.find_all_by_user_id(user_id)

    return jsonify({
        "success": True,
        "user": {
            "fullName": user.name,
            "email": user.email,
            "resumeCount": len(resumes),
        },
        "resumes": [
            {
                "resumeId": str(resume["_id"]),
                "fileName": resume.get("file_name", "Unknown"),
                "createdAt": resume.get("created_at", "Unknown")
            }
            for resume in resumes
        ]
    }), 200

# Update user profile details
@user_routes.route("/profile", methods=["PUT"])
def update_user_profile():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    # Verify JWT token
    payload = verify_jwt_token(token)
    if isinstance(payload, str):  # If payload is a string, it's an error message
        return jsonify({"error": payload}), 401

    user_id = payload.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 400

    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    name = data.get("name")
    email = data.get("email")
    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")

    # Update name
    if name:
        user.name = name

    # Update email
    if email and email != user.email:
        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify({"error": "Email already in use"}), 400
        user.email = email

    # Update password
    if new_password:
        if not current_password or not user.verify_password(current_password):
            return jsonify({"error": "Current password is incorrect"}), 401
        user.password = new_password

    user.save()

    return jsonify({"success": True, "message": "Profile updated successfully"}), 200

# Fetch specific resume details
@user_routes.route("/resume/<resume_id>", methods=["GET"])
def get_resume_details(resume_id):
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    # Verify JWT token
    payload = verify_jwt_token(token)
    if isinstance(payload, str):  # If payload is a string, it's an error message
        return jsonify({"error": payload}), 401

    user_id = payload.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 400

    resume = Resume.find_by_id_and_user_id(resume_id, user_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    return jsonify({
        "success": True,
        "resume": {
            "resumeId": str(resume["_id"]),
            "fileName": resume.get("file_name", "Unknown"),
            "createdAt": resume.get("created_at", "Unknown"),
            "content": resume.get("content", "No content available")
        }
    }), 200

# Delete a resume
@user_routes.route("/resume/<resume_id>", methods=["DELETE"])
def delete_resume(resume_id):
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    # Verify JWT token
    payload = verify_jwt_token(token)
    if isinstance(payload, str):  # If payload is a string, it's an error message
        return jsonify({"error": payload}), 401

    user_id = payload.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 400

    resume = Resume.find_by_id_and_user_id(resume_id, user_id)
    if not resume:
        return jsonify({"error": "Resume not found or access denied"}), 404

    try:
        # Use `get_db()` to access the database
        db = get_db()
        db.resumes.delete_one({"_id": ObjectId(resume_id)})
        return jsonify({"success": True, "message": "Resume deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete resume: {str(e)}"}), 500

# Delete user account and associated resumes
@user_routes.route("/account", methods=["DELETE"])
def delete_account():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    # Verify JWT token
    payload = verify_jwt_token(token)
    if isinstance(payload, str):  # If payload is a string, it's an error message
        return jsonify({"error": payload}), 401

    user_id = payload.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 400

    db = get_db()
    db.resumes.delete_many({"user_id": user_id})
    db.users.delete_one({"_id": ObjectId(user_id)})

    return jsonify({"success": True, "message": "Account and associated resumes deleted successfully"}), 200
