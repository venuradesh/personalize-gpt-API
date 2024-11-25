from typing import Any, Dict, Tuple
from firebase_admin import firestore
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