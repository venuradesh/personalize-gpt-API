from typing import Dict, List
from langchain.schema import Document
import openai
from flask import session
from Helpers import user_api_key
from Helpers.document_parser import retrieve_document_chunks, upload_document
from Helpers.langchain import LangchainHelper
from Helpers.user_api_key import UserAPIKey
from models.ChatHistory import ChatHistory
from services import assistant_service
from services.assistant_service import AssistantService
from services.user_service import UserService

class DocAnalyzerService:
    def __init__(self) -> None:
        self.user_api_key = UserAPIKey()
        self.user_service = UserService()
        self.chat_history = ChatHistory()
        self.DOC_ANALYZER_VECTOR_DB_PATH_KEY = 'doc_vector_db_path_key'

    def upload_document(self, user_id: str, file) -> Dict:
        try:
            file_name = file.filename.rsplit('.', 1)[0]
            vector_db_path = f"./vector_index/{user_id}/{file_name}"
            session[self.DOC_ANALYZER_VECTOR_DB_PATH_KEY] = vector_db_path
            session['file_name'] = file_name

            upload_document(file, vector_db_path, user_id)

            return {'message': 'Document processed and stored successfully', 'error': False, 'data': None}

        except Exception as e:
            raise e
        
    def generate_response(self, user_id: str, query: str) -> Dict:
        try:
            vector_db_path = session[self.DOC_ANALYZER_VECTOR_DB_PATH_KEY]
            choosen_llm = self.user_api_key.get_user_choosen_api(user_id)

            if choosen_llm.lower() == 'openai':
                response = self._generate_openai_assistant_response(user_id, query)

            else:
                retrieved_docs = retrieve_document_chunks(user_id, vector_db_path, query)
                response = self._generate_document_response(user_id, query, retrieved_docs)

            self.chat_history.save_doc_messages(user_id, query, response)
            return {'message': 'Query Processed', 'data': response, 'error': False}

        except Exception as e:
            raise e
        

    def load_doc_session_chats(self, user_id):
        try:
            file_name = session.get('file_name', '')
            file_extension = session.get('file_extension', 'pdf')
            if not file_name:
                return {'file_name': '', 'chat': []}
            else:
                return {'file_name': f"{file_name}.{file_extension}", 'chat':self.chat_history.get_doc_chat_history(user_id)}

        except Exception as e:
            raise e


    def _generate_document_response(self, user_id: str, user_query: str, retrieved_docs: List[Document]) -> str:
        try:
            choosen_llm = self.user_api_key.get_user_choosen_api(user_id)
            api_key = self.user_api_key.get_user_api_key(user_id, choosen_llm)

            llm = LangchainHelper.initialize_llm(choosen_llm, api_key)
            user_details = self.user_service.get_user_profile(user_id)
            chat_history = self.chat_history.get_doc_chat_history(user_id)

            prompt = LangchainHelper.generate_doc_prompt(user_query, retrieved_docs, chat_history, user_details)
            response = llm.predict(prompt)


            return response

        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
        

    def _generate_openai_assistant_response(self, user_id: str, query: str) -> str:
        try:
            file_id = session['openai_file_id']
            if not file_id:
                raise ValueError("No document uploaded to openAI Assistant.")
            
            api_key = self.user_api_key.get_user_openai_api_key(user_id)
            assistant_response = AssistantService.process_query(query, user_id, api_key)
            
            return assistant_response

        except Exception as e:
            raise Exception(f"Error in OpenAI Assistant response: {str(e)}")

        