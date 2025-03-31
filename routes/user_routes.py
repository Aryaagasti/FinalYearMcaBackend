from flask import Blueprint, request, jsonify
from models.user_model import User
from utils.jwt_utils import verify_jwt_token

user_routes = Blueprint("user_routes", __name__)

@user_routes.route("/details", methods=["GET"])
def get_user_details():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    # Verify JWT token
    payload = verify_jwt_token(token)
    if isinstance(payload, str):  # If payload is a string, it's an error message
        return jsonify({"error": payload}), 401

    user_email = payload.get("email")  # Get email from token
    if not user_email:
        return jsonify({"error": "Email not found in token"}), 400

    # Fetch user from database using the correct MongoDB method
    user = User.find_by_email(user_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "email": user.email,
        "name": user.name
    }), 200
