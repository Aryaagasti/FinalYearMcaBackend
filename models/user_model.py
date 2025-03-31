from datetime import datetime
from config.db import init_db

def get_db():
    from app import app  # Avoid circular imports
    return init_db(app).db

class User:
    def __init__(self, email, name, password, created_at=None):
        self.email = email
        self.name = name
        self.password = password  # Plaintext password (use hashing in production)
        self.created_at = created_at if created_at else datetime.now()

    def save(self):
        db = get_db()
        db.users.insert_one(self.__dict__)

    @staticmethod
    def find_by_email(email):
        db = get_db()
        user_data = db.users.find_one({"email": email})
        
        if user_data:
            return User(
                email=user_data["email"],
                name=user_data["name"],
                password=user_data["password"],
                created_at=user_data.get("created_at")
            )
        return None

    def verify_password(self, provided_password):
        return self.password == provided_password  # Use hashing in production
