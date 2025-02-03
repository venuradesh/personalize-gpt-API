from typing import Dict, List
from langchain.schema import Document

from flask import session
from Helpers.document_parser import extract_text_from_file, split_text_into_chunks, retrieve_document_chunks
from Helpers.langchain import LangchainHelper
from Helpers.user_api_key import UserAPIKey
from Helpers.vector_db import VectorDBHelper
from models.ChatHistory import ChatHistory
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

            extracted_text = extract_text_from_file(file)
            text_chunks = split_text_into_chunks(extracted_text)

            index = VectorDBHelper.create_or_load_index(vector_db_path, user_id)
            VectorDBHelper.add_documents_to_index(index, text_chunks)

            return {'message': 'Document processed and stored successfully', 'error': False, 'data': None}

        except Exception as e:
            raise e
        
    def generate_response(self, user_id: str, query: str) -> Dict:
        try:
            vector_db_path = session[self.DOC_ANALYZER_VECTOR_DB_PATH_KEY]
            retrieved_docs = retrieve_document_chunks(user_id, vector_db_path, query)
            response = self._generate_document_response(user_id, query, retrieved_docs)

            return {'message': 'Query Processed', 'data': response, 'error': False}

        except Exception as e:
            raise e

    def _generate_document_response(self, user_id: str, user_query: str, retrieved_docs: List[Document]) -> str:
        try:
            choosen_llm = self.user_api_key.get_user_choosen_api(user_id)
            api_key = self.user_api_key.get_user_api_key(user_id, choosen_llm)

            llm = LangchainHelper.initialize_llm(choosen_llm, api_key)
            user_details = self.user_service.get_user_profile(user_id)
            chat_history = self.chat_history.get_doc_chat_history(user_id)

            prompt = LangchainHelper.generate_prompt(user_query, retrieved_docs, chat_history, user_details)
            response = llm.predict(prompt)

            self.chat_history.save_doc_messages(user_id, user_query, response)

            return response

        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

        