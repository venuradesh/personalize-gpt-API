
from custom_types.UserDetails import APIKeys, UserDetails
from utils.password_utils import hash_password
from google.cloud.firestore import Client

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
            openai_api_key= data_as_json.get('openai_api_key'),
            llama_api_key=data_as_json.get('llama_api_key')
        ),
    )

def is_email_exists(db: Client, collection:str , email: str):
    user_data = db.collection(collection).where('email', '==', email).limit(1)
    return any(user_data.stream())

