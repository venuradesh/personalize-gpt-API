from typing import List
from PyPDF2 import PdfReader
from flask import session
from langchain.text_splitter import RecursiveCharacterTextSplitter

from Helpers.user_api_key import UserAPIKey
from Helpers.vector_db import VectorDBHelper
import openai
from services.assistant_service import AssistantService

def extract_text_from_file(file) -> str:
    try:
        if file.mimetype == 'application/pdf':
            reader = PdfReader(file)
            return ' '.join([page.extract_text() for page in reader.pages])
        else:
            raise ValueError('Unsupported file type. Only PDFs are supported at the moment')
    
    except Exception as e:
        raise e
    

def split_text_into_chunks(text: str, chunk_size: int = 700, overlap: int = 50) -> List:
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            separators=["\n\n", "\n", ".", "!", "?"]
        )
        return splitter.split_text(text)

    except Exception as e:
        raise Exception(f"Error splitting text into chunks: {str(e)}")
    

def retrieve_document_chunks(user_id: str, vector_db_path: str, query: str, top_k: int = 10):
    try:
        index = VectorDBHelper.create_or_load_index(vector_db_path, user_id)
        return VectorDBHelper.search_index(index, query, top_k)
    except Exception as e:
        raise Exception(f"Error retrieving document chunks: {str(e)}")
    

def upload_document(file, vector_db_path: str, user_id: str) -> None:
    try:
        user_api_key = UserAPIKey()
        choosen_llm = user_api_key.get_user_choosen_api(user_id)

        if choosen_llm.lower() == 'openai':
            api_key = user_api_key.get_user_api_key(user_id, choosen_llm)
            openai_file_id = AssistantService.upload_file_to_openai(file, api_key)
            session['openai_file_id'] = openai_file_id
            session['openai_thread_id'] = None #reseting the thread id when a new file uploaded 

        else:
            extracted_text = extract_text_from_file(file)
            text_chunks = split_text_into_chunks(extracted_text)

            index = VectorDBHelper.create_or_load_index(vector_db_path, user_id)
            VectorDBHelper.add_documents_to_index(index, text_chunks, vector_db_path)

    except Exception as e:
        raise e