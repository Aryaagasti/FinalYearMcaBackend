from flask import Blueprint, request, jsonify
from models.user_model import User
from utils.jwt_utils import create_jwt_token, verify_jwt_token
import json

auth_routes = Blueprint("auth_routes", __name__)

@auth_routes.route("/register", methods=["POST"])
def register():
    # Check if request has JSON data
    if not request.data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        data = request.get_json()
    except:
        return jsonify({"error": "Invalid JSON format"}), 400

    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    if not all([email, name, password]):
        return jsonify({"error": "Missing required fields"}), 400

    if User.find_by_email(email):
        return jsonify({"error": "User already exists"}), 409

    user = User(email, name, password)
    user.save()

    token = create_jwt_token(str(user.id))

    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": str(user.id),
            "email": email,
            "name": name
        }
    }), 201

@auth_routes.route("/login", methods=["POST"])
def login():
    # Check if request has JSON data
    if not request.data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        data = request.get_json()
    except:
        return jsonify({"error": "Invalid JSON format"}), 400

    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Missing email or password"}), 400

    user = User.find_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.verify_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_jwt_token(str(user.id))

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    }), 200

@auth_routes.route("/protected", methods=["GET"])
def protected():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid authorization header"}), 401

    token = auth_header.split(" ")[1]
    verification = verify_jwt_token(token)
    
    if isinstance(verification, dict) and "error" in verification:
        return jsonify({"error": verification["error"]}), 401
    
    user_id = verification.get("user_id")
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "message": "Protected endpoint accessed successfully",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    }), 200