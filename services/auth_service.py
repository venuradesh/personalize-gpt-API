from firebase_admin import firestore
from flask import jsonify

class AuthService:
    def __init__(self):
        self.db = firestore.client()
        self.USERS_COLLECTION = 'pgpt-users'


    def authenticate_user(self, email, password):
        try:
            user_data = self.get_user_by_email(email)

            return {"message": 'Authentication successful', "data": user_data, "error": False}, 200

        except Exception as e:
            return {"message": str(e), "data": {}, "error": True}, 401
        

    def get_user_by_email(self, email):
        try:
            user_ref = self.db.collection(self.USERS_COLLECTION)
            user = user_ref.where('email', '==', email).limit(1).get()

            if not user:
                raise ValueError("User not found")
            
            return user[0].to_dict()

        except ValueError as e:
            raise e

        except Exception as e:
            raise RuntimeError(f"Error fetcing user with email: {email}")