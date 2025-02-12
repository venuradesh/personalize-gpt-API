from firebase_admin import firestore
from Helpers.Common import decrypt_data

class UserAPIKey:
    def __init__(self) -> None:
        self.db = firestore.client()
        self.USERS_COLLECTION = 'pgpt-users'
        self.user_collection = self.db.collection(self.USERS_COLLECTION)

    def get_user_choosen_api(self, user_id: str) -> str: 
        try:
            user_doc = self.user_collection.document(user_id).get()

            if user_doc.exists:
                return user_doc.get('choosen_llm')
            raise Exception('No chosen LLM found. Please select one to proceed')

        except Exception as e:
            raise e    


    def get_user_openai_api_key(self, user_id: str) -> str:
        try:
            user_doc = self.user_collection.document(user_id).get()

            if user_doc.exists:
                openai_encyrpted_key = user_doc.get('api_keys').get('openai_api_key')
                return decrypt_data(openai_encyrpted_key)
            raise Exception("No OpenAI key found. Please provide a valid key to proceed")
            
        except Exception as e:
            raise e
        
    
    def get_user_llama_api_key(self, user_id: str) -> str:
        try:
            user_doc = self.user_collection.document(user_id).get()

            if user_doc.exists:
                llama_encrypted_key = user_doc.get('api_keys').get('llama_api_key')
                return decrypt_data(llama_encrypted_key)
            raise Exception("No GroqCloud API key found. Please provide a valid key to proceed")
            
        except Exception as e:
            raise e
        
    
    def get_user_api_key(self, user_id: str, choosen_llm: str) -> str:
        if choosen_llm.lower() == 'openai':
            return self.get_user_openai_api_key(user_id)
        elif choosen_llm.lower() == 'llama-3.1':
            return self.get_user_llama_api_key(user_id)
        else:
            raise ValueError("Invalid LLM selected")