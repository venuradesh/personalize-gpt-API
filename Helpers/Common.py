
from datetime import datetime, timezone
import os
import pytz
from custom_types.UserDetails import APIKeys, UserDetails, UserProfile
from utils.password_utils import hash_password
from google.cloud.firestore import Client
from cryptography.fernet import Fernet

def convert_json_to_user_details(data_as_json) -> UserDetails:
    return UserDetails(
        first_name = data_as_json.get("first_name"),
        last_name = data_as_json.get("last_name"),
        date_of_birth = data_as_json.get("date_of_birth"),
        email = data_as_json.get("email"),
        company_name = data_as_json.get("company_name"),
        job_title = data_as_json.get("job_title"),
        country = data_as_json.get('country'),
        hashed_password = hash_password(data_as_json.get("password")),
        personality = data_as_json.get("personality"),
        description = data_as_json.get("description"),
        choosen_llm = data_as_json.get('choosen_llm'),
        api_keys = APIKeys(
            openai_api_key = encrypt_data(data_as_json.get('openai_api_key')),
            llama_api_key = encrypt_data(data_as_json.get('llama_api_key'))
        ),
    )

def is_email_exists(db: Client, collection:str , email: str):
    user_data = db.collection(collection).where('email', '==', email).limit(1)
    return any(user_data.stream())


def get_user_profile(db: Client, user_id: str) -> UserProfile:
    user_data = db.collection('pgpt-users').document(user_id).get()
    if not user_data:
        raise ValueError('User not found')
    
    user_dict = user_data.to_dict()
    if not user_dict:
        raise ValueError('User data is missing or invalid')
    
    user_dict['_id'] = user_data.id
    return get_user_profile_from_user_details(UserDetails(**user_dict))


def encrypt_data(value: str) -> (str):
    if not value:
        return ""
    try:
        key = os.environ.get('FERNET_KEY', '')
        fernet = Fernet(key.encode())
        encrypted_data = fernet.encrypt(value.encode())
        return encrypted_data.decode()
    
    except Exception as e:
        raise Exception("Server Error Occured while encrypting the keys")



def decrypt_data(encrypted_value: str) -> str:
    if not encrypt_data:
        return ""
    
    try:
        key = os.environ.get('FERNET_KEY', '')
        fernet = Fernet(key.encode())
        decrupted_data = fernet.encrypt(encrypted_value.encode())
        return decrupted_data.decode()
    
    except Exception as e:
        raise Exception("Server Error Occured while encrypting the keys")
    

def get_user_profile_from_user_details(user_details: UserDetails) -> UserProfile:
    return UserProfile(
        _id=user_details._id,
        first_name=user_details.first_name,
        last_name=user_details.last_name,
        date_of_birth=user_details.date_of_birth,
        email=user_details.email,
        job_title=user_details.job_title,
        country=user_details.country,
        personality=user_details.personality,
        description=user_details.description or ""
    )


def format_date_to_gmt() -> str:
    utc_now = datetime.now(timezone.utc)
    formatted_date = utc_now.strftime("%a %b %d %Y %H:%M:%S GMT%z")
    return formatted_date
