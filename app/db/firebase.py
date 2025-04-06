import os
import json
import firebase_admin
from firebase_admin import credentials, db
from app.config import FIREBASE_URL


# Get Firebase credentials from environment variable as JSON
def get_firebase_credentials():
    firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

    if not firebase_credentials_json:
        raise ValueError("FIREBASE_CREDENTIALS_JSON environment variable is not set")

    try:
        return json.loads(firebase_credentials_json)
    except json.JSONDecodeError:
        raise ValueError("Invalid FIREBASE_CREDENTIALS_JSON format")


# Initialize Firebase Admin SDK with credentials from environment variables
cred = credentials.Certificate(get_firebase_credentials())
firebase_app = firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_URL
})


# Helper class to wrap Firebase Realtime Database operations with chaining
class DatabaseReference:
    def __init__(self, ref=None):
        self.ref = ref if ref else db.reference()

    def child(self, path):
        return DatabaseReference(self.ref.child(path))

    def get(self):
        return self.ref.get()

    def set(self, data):
        self.ref.set(data)

    def update(self, data):
        self.ref.update(data)


# Database reference wrapper
database = DatabaseReference()