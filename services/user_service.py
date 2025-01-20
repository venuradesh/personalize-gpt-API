from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Tuple
from firebase_admin import firestore
from flask_jwt_extended import get_jwt_identity
from Helpers.Common import convert_json_to_user_details
from custom_types.UserDetails import UserDetails
from models.UserModel import User


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
            user_update_details['last_update'] = datetime.now()

            user_doc_ref = self.db.collection(self.USERS_COLLECTION).document(user_id)
            user_doc_ref.update(user_update_details)

            return {"message": "Updated Successfully", "data": None, "error": False}, 202

        except Exception as e:
            raise e
        

    def update_llm_modal_and_keys(self, changed_llm: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        try:
            user_id = get_jwt_identity()
            llm_update_details = {
                "choosen_llm": "",
                "api_keys": {}
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
            llm_update_details['api_keys'][choosen_api_key] = changed_llm['api_key'] if not llm_update_details['api_keys'][choosen_api_key] else llm_update_details["api_keys"][choosen_api_key]

            user_doc_ref.update(llm_update_details)

            return {"message": "LLM Changed Successfully", "data": None, "error": False}, 202

        except Exception as e:
            raise e



       
