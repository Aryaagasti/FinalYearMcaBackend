from flask import Blueprint, request, jsonify
from models.user_model import User
from utils.jwt_utils import create_jwt_token

auth_routes = Blueprint("auth_routes", __name__)

@auth_routes.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    if not email or not name or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if user already exists
    if User.find_by_email(email):
        return jsonify({"error": "User already exists"}), 400

    # Create new user and save to DB
    user = User(email, name, password)
    user.save()

    # Generate JWT token
    token = create_jwt_token({"email": email})  # Use email as the unique identifier
    return jsonify({"message": "User registered successfully", "token": token}), 201

@auth_routes.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Find user
    user = User.find_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Verify password
    if not user.verify_password(password):
        return jsonify({"error": "Invalid password"}), 401

    # Generate JWT token
    token = create_jwt_token({"email": email})  # Use email as the unique identifier
    return jsonify({"message": "Login successful", "token": token}), 200
