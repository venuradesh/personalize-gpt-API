from typing import Dict
from uuid import uuid4

from flask import session
from Helpers.langchain import LangchainHelper
from Helpers.user_api_key import UserAPIKey
from firebase_admin import firestore
from Helpers.Common import get_user_profile, format_date_to_gmt

from models.ChatHistory import ChatHistory


class ChatService:
    def __init__(self) -> None:
        self.user_apikey = UserAPIKey()
        self.chat_history = ChatHistory()
        self.db = firestore.client()

    def get_user_api_key(self, user_id: str, choosen_llm: str) -> str:
        if choosen_llm.lower() == 'openai':
            return self.user_apikey.get_user_openai_api_key(user_id)
        elif choosen_llm.lower() == 'llama-3.1':
            return self.user_apikey.get_user_llama_api_key(user_id)
        else:
            raise ValueError("Invalid LLM selected")
        
    def generate_response(self, user_id: str, user_input: str) -> Dict: 
        try:
            choosen_llm = self.user_apikey.get_user_choosen_api(user_id)
            api_key = self.get_user_api_key(user_id, choosen_llm)

            # Initialize LLM
            llm = LangchainHelper.initialize_llm(choosen_llm, api_key)
            retriever = LangchainHelper.create_retriever(user_id, top_k=3)
            retrieved_docs = retriever.get_relevant_documents(user_input)
            user_profile = get_user_profile(self.db, user_id)
            chat_history = self.chat_history.get_chat_history(user_id)

            # generate prompt
            prompt = LangchainHelper.generate_prompt(user_input, retrieved_docs, chat_history, user_profile)
            response = llm.predict(prompt)

            chat_id = self.chat_history.save_messages(user_id, user_input, response)

            return { "response": response, "chat_id": chat_id, 'created': format_date_to_gmt() }

        except Exception as e:
            raise Exception(f"Error occured while genearting the Response: {str(e)}")
        
    def load_session_chat(self, user_id):
        try:
            if 'chat_id' not in session:
                return []
            return ChatHistory().get_chat_history(user_id)

        except Exception as e:
            raise Exception("No session chat available")
        

    def get_new_chat(self) -> None:
        session.clear()
        session['chat_id'] = str(uuid4())

        return None