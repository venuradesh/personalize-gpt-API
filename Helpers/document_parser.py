from typing import List
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from Helpers.vector_db import VectorDBHelper

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
    

def retrieve_document_chunks(user_id: str, vector_db_path: str, query: str, top_k: int = 5):
    try:
        index = VectorDBHelper.create_or_load_index(vector_db_path, user_id)
        return VectorDBHelper.search_index(index, query, top_k)
    except Exception as e:
        raise Exception(f"Error retrieving document chunks: {str(e)}")