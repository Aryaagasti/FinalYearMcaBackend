from datetime import datetime
from bson import ObjectId
from config.db import init_db

def get_db():
    from app import app
    return init_db(app).db

class Resume:
    def __init__(self, user_id, resume_text, ats_score, keywords, suggestions):
        self.user_id = user_id
        self.resume_text = resume_text
        self.ats_score = ats_score
        self.keywords = keywords
        self.suggestions = suggestions
        self.created_at = datetime.now()
    
    def save(self):
        db = get_db()
        db.resumes.insert_one(self.__dict__)
    
    @staticmethod
    def find_all_by_user_id(user_id):
        db = get_db()
        # Returns all resumes associated with the user ID
        return list(db.resumes.find({"user_id": user_id}))

    @staticmethod
    def find_by_id_and_user_id(resume_id, user_id):
        db = get_db()
        return db.resumes.find_one({"_id": ObjectId(resume_id), "user_id": user_id})
