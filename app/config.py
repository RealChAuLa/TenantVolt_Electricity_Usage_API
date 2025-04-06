import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Firebase configuration
FIREBASE_URL = os.getenv("FIREBASE_URL")
if not FIREBASE_URL:
    raise ValueError("FIREBASE_URL environment variable is not set. This is required for Firebase operations.")

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
if not FIREBASE_API_KEY:
    raise ValueError("FIREBASE_API_KEY environment variable is not set. This is required for Firebase operations.")
