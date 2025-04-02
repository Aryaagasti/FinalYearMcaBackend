import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get secret key from environment
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY must be set in environment variables")

logger.info(f"Loaded SECRET_KEY: {SECRET_KEY[:5]}*****")  # Partially log secret for debugging

def create_jwt_token(user_id, expires_days=30):
    """Create a JWT token with expiration."""
    try:
        payload = {
            "user_id": str(user_id),  # Ensure user_id is string
            "exp": datetime.utcnow() + timedelta(days=expires_days),
            "iat": datetime.utcnow()  # Issued at time
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        logger.info(f"Token created for user {user_id}: {token[:20]}...")  # Partial logging for security
        return token
    except Exception as e:
        logger.error(f"Token creation failed: {str(e)}")
        return None

def verify_jwt_token(token):
    """Verify JWT token and return payload if valid."""
    try:
        if not token:
            logger.warning("Empty token provided")
            return {"error": "Token is missing"}

        # Remove 'Bearer ' prefix if present
        token = token.replace("Bearer ", "").strip()
        
        # Log token before verification
        logger.info(f"Verifying token: {token[:20]}...")  # Partial log for debugging

        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        if not payload.get("user_id"):
            logger.warning("Token missing user_id")
            return {"error": "Invalid token payload"}
            
        logger.info(f"Token verified for user {payload['user_id']}")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Expired token")
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return {"error": "Token verification failed: Signature verification failed"}
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return {"error": "Token verification failed"}
