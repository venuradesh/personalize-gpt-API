from dataclasses import dataclass
from typing import Any, Dict, Tuple
from firebase_admin import firestore
from flask_jwt_extended import get_jwt_identity
from Helpers.Common import convert_json_to_user_details, get_user_profile, encrypt_data, decrypt_data, get_user_profile_from_user_details
from custom_types.UserDetails import UserDetails, UserProfile
from google.cloud.firestore import Client
from models.UserModel import User
from utils.password_utils import hash_password


class UserService:
    def __init__(self) -> None:
        self.db = firestore.client()
        self.USERS_COLLECTION = 'pgpt-users'


    def get_user_details(self, user_id) -> dict:
        try:
            document_ref = self.db.collection(self.USERS_COLLECTION).document(user_id)
            document_snapshot = document_ref.get()

            if(document_snapshot):
                data = document_snapshot.to_dict()
                if not data:
                    raise ValueError("No data available")
                data['_id'] = document_snapshot.id

                return UserDetails(**data).to_user_profile_dict()
            
            else:
                raise ValueError("No data available")
        
        except Exception as e:
            raise e
        

    def register_user(self, data_as_json) -> Tuple[Dict[str, Any], int]:
        try:
            user_details: UserDetails = convert_json_to_user_details(data_as_json)
            new_user = User(user_details=user_details)
            
            return new_user.save()
        except Exception as e:
            raise e
        

    def update_user_info(self, user_id: str, user_details: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        try:
            user_update_details = {key: value for key, value in user_details.items() if value is not None }
            user_update_details['last_update'] = firestore.firestore.SERVER_TIMESTAMP

            user_doc_ref = self.db.collection(self.USERS_COLLECTION).document(user_id)
            user_doc_ref.update(user_update_details)

            return {"message": "Updated Successfully", "data": None, "error": False}, 202

        except Exception as e:
            raise e
        

    def get_user_profile(self, user_id) -> UserProfile:
        try:
            return get_user_profile(self.db, user_id)
        
        except Exception as e:
            raise e
        

    def update_llm_modal_and_keys(self, changed_llm: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        try:
            user_id = get_jwt_identity()
            llm_update_details = {
                "choosen_llm": "",
                "api_keys": {},
                "last_update": firestore.firestore.SERVER_TIMESTAMP
            }

            user_doc_ref = self.db.collection(self.USERS_COLLECTION).document(user_id)
            user_doc_snapshot = user_doc_ref.get()

            if not user_doc_snapshot.exists:
                raise ValueError("User not found")
            
            # Setting the previous api keys as it is
            llm_update_details["api_keys"] = user_doc_snapshot.get('api_keys')

            choosen_api_key = "llama_api_key" if changed_llm['choosen_llm'] == 'Llama-3.1' else 'openai_api_key' if changed_llm['choosen_llm'] == 'OpenAI' else ''
            if not choosen_api_key:
                raise ValueError("Invalid API Choosen")
            
            llm_update_details['choosen_llm'] = changed_llm['choosen_llm']

            if not llm_update_details["api_keys"][choosen_api_key] and not changed_llm['api_key']:
                raise ValueError(f"You don't have any f{changed_llm['choosen_llm']} key specified.")
            
            if changed_llm["api_key"]:
               llm_update_details["api_keys"][choosen_api_key] = encrypt_data(changed_llm["api_key"]) 

            user_doc_ref.update(llm_update_details)

            return {"message": "LLM Changed Successfully", "data": None, "error": False}, 202

        except Exception as e:
            raise e
        
    
    def authenticate_user_by_token(self, reset_token:str) -> tuple[str, str]:
        try:
            user_email, user_id = self.get_user_email_by_refresh_token(reset_token)
            return user_email, user_id

        except Exception as e:
            raise e
    

    def reset_passwords(self, user_id: str, password: str):
        try:
            document_ref = self.db.collection(self.USERS_COLLECTION).document(user_id)
            document_snapshot = document_ref.get()

            if(document_snapshot):
                hashed_password = hash_password(password)
                self.update_a_specific_key(user_id, 'hashed_password', hashed_password)
                self.update_a_specific_key(user_id, 'reset_token', None)
                
            else:
                raise ValueError("No data available")
            

        except Exception as e:
            raise e


    def get_user_profile_by_email(self, email: str) -> UserProfile:
        try:
            user_collection = self.db.collection(self.USERS_COLLECTION)
            query = user_collection.where('email', '==', email).limit(1).get()

            if not query:
                raise ValueError("User email not found")
            
            user_data = query[0]
            user_dict = user_data.to_dict()
            if not user_dict:
                raise ValueError("User data is missing or invalid")
            
            user_dict['_id'] = user_data.id
            return get_user_profile_from_user_details(UserDetails(**user_dict))

        except Exception as e:
            raise e
        

    def get_user_email_by_refresh_token(self, reset_token: str) -> tuple[str, str]:
        try:
            user_collection = self.db.collection(self.USERS_COLLECTION)
            query = user_collection.where('reset_token', '==', reset_token).limit(1).get()

            if not query:
                raise ValueError("Not a valid reset token")
            
            user_data = query[0]
            user_dict = user_data.to_dict()
            if not user_dict:
                raise ValueError("Not a valid reset token")
            
            return user_dict['email'], user_data.id

        except Exception as e:
            raise e
        

    def update_a_specific_key(self, user_id: str, key: str, value: Any) -> None:
        try:
            user_doc_ref = self.db.collection(self.USERS_COLLECTION).document(user_id)
            user_doc = user_doc_ref.get()
            if not user_doc:
                raise ValueError("No user detail found")
            
            user_doc_ref.update({key: value, 'last_update': firestore.firestore.SERVER_TIMESTAMP})

        except Exception as e:
            raise e



       
