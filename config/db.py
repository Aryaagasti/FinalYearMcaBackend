from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv

load_dotenv()

# Global variable for PyMongo
mongo = None

def init_db(app):
    """
    Initialize MongoDB using Flask app and return the PyMongo instance.
    """
    global mongo
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")  # Load Mongo URI from .env
    mongo = PyMongo(app)  # Initialize PyMongo with the Flask app
    return mongo

def get_db():
    """
    Get the MongoDB database instance. Ensure `init_db` is called first.
    """
    global mongo
    if not mongo:
        raise RuntimeError("Database is not initialized. Call `init_db(app)` first.")
    return mongo.db  # Return the MongoDB instance
