from datetime import datetime
from bson import ObjectId  # Import ObjectId for MongoDB
from config.db import init_db

def get_db():
    from app import app  # Avoid circular imports
    return init_db(app).db

class User:
    def __init__(self, email, name, password, _id=None, created_at=None):
        self._id = _id if _id else ObjectId()  # MongoDB uses _id
        self.email = email
        self.name = name
        self.password = password  # Plaintext password (use hashing in production)
        self.created_at = created_at if created_at else datetime.now()

    @property
    def id(self):
        return str(self._id)  # Provide id property that returns string version

    def save(self):
        db = get_db()
        # Convert to dict and remove _id if None to let MongoDB generate it
        user_data = self.__dict__.copy()
        if user_data['_id'] is None:
            del user_data['_id']
        result = db.users.insert_one(user_data)
        self._id = result.inserted_id  # Update with the generated _id
        return self

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
        return self.password == provided_password  # Use hashing in production