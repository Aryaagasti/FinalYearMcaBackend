import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY must be set in environment variables")

def create_jwt_token(user_id, expires_days=365):  # 1 year expiration by default
    """Create a JWT token with expiration"""
    payload = {
        "user_id": user_id,
        "exp": datetime.now() + timedelta(days=expires_days)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_jwt_token(token):
    """Verify JWT token and return payload if valid"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}
    except Exception as e:
        return {"error": str(e)}