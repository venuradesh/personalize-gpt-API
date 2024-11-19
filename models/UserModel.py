from datetime import datetime
from custom_types.UserDetails import UserDetails
from firebase_admin import firestore
from Helpers.Common import is_email_exists


class User:
    def __init__(self, user_details: UserDetails):
        self.db = firestore.client()
        self.user_details = user_details
        self.USER_COLLECTION = "pgpt-users"


    def save(self):
        try:
            is_email_available = is_email_exists(self.db, self.USER_COLLECTION, self.user_details.email)
            if is_email_available:
                raise ValueError('Email already exists')
            
            user_details = self.user_details.to_dict()
            user_details['created'] = user_details.get('created') or datetime.now()
            user_details['last_update'] = datetime.now()

            self.db.collection(self.USER_COLLECTION).add(user_details)

            return {"message": "Successfully created", "data": None, "error": False}, 201

        except ValueError as e:
            return {"message": str(e), "data": None, "error": True}, 403
