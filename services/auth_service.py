from os import access
from typing import Any, Dict, Tuple
from firebase_admin import firestore
from flask import jsonify, session
from flask_jwt_extended import create_access_token, create_refresh_token

from custom_types.UserDetails import UserDetails
from utils.password_utils import validate_password

class AuthService:
    def __init__(self):
        self.db = firestore.client()
        self.USERS_COLLECTION = 'pgpt-users'


    def authenticate_user(self, email, password) -> Tuple[Dict[str, Any], int] :
        try:
            user_data: UserDetails = self.get_user_by_email(email)
            is_valid_password: bool = validate_password(user_data.hashed_password, password)
            session.clear()  
            
            if not is_valid_password:
                return {"message": "Password is incorrect", "data": None, "error": True}, 401

            # Set Access and Refresh tokens
            if not user_data._id:
                return {"message": "Cannot set Access token, Try again.", "data": None, "error": True}, 401

            #set access Tokens
            access_token, refresh_token = self.set_access_tokens(user_data._id)
            return {"message": 'Authentication successful', "data": {"user_id": user_data._id}, "access_token": access_token, "refresh_token": refresh_token, "error": False}, 200

        except Exception as e:
            return {"message": str(e), "data": {}, "error": True}, 401
        


    def get_user_by_email(self, email) -> UserDetails:
        try:
            user_ref = self.db.collection(self.USERS_COLLECTION)
            user = user_ref.where('email', '==', email).limit(1).get()

            #If no user found
            if not user:
                raise ValueError("User not found")
            
            user_dict = user[0].to_dict()
            # Check if the user_dict is None
            if not user_dict:
                raise ValueError("User data is missing or invalid")
            
            # Add the user document id as user_id
            user_dict['_id'] = user[0].id
            return UserDetails(**user_dict)

        except ValueError as e:
            raise e

        except Exception as e:
             raise RuntimeError(f"Error fetcing user with email: {email}")



    def set_access_tokens(self, user_id: str) -> tuple[str, str]:
        try:
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)

            self.db.collection(self.USERS_COLLECTION).document(user_id).update({"access_token":access_token, "refresh_token": refresh_token})

            return access_token, refresh_token

        except Exception as e:
            raise e