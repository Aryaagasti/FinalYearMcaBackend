from datetime import datetime
from bson import ObjectId  # For MongoDB ObjectId
from config.db import get_db  # Import the database initialization

class User:
    def __init__(self, email, name, password, _id=None, created_at=None):
        self._id = _id if _id else ObjectId()  # MongoDB uses ObjectId for unique identifiers
        self.email = email
        self.name = name
        self.password = password  # Plaintext password (use hashing in production)
        self.created_at = created_at if created_at else datetime.now()

    @property
    def id(self):
        return str(self._id)  # Provide a string version of _id for APIs

    def save(self):
        db = get_db()
        # Use update_one with upsert=True to update or insert the user
        db.users.update_one(
            {"_id": self._id},  # Match the document by _id
            {"$set": self.__dict__},  # Update fields
            upsert=True  # Insert if it doesn't exist
        )

    @staticmethod
    def find_by_email(email):
        db = get_db()
        user_data = db.users.find_one({"email": email})
        if user_data:
            return User(
                email=user_data["email"],
                name=user_data["name"],
                password=user_data["password"],
                _id=user_data["_id"],
                created_at=user_data.get("created_at")
            )
        return None

    @staticmethod
    def find_by_id(user_id):
        db = get_db()
        try:
            user_data = db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User(
                    email=user_data["email"],
                    name=user_data["name"],
                    password=user_data["password"],
                    _id=user_data["_id"],
                    created_at=user_data.get("created_at")
                )
        except:
            return None
        return None

    def verify_password(self, provided_password):
        return self.password == provided_password  # This should use secure password hashing in production
