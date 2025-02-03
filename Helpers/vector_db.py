from importlib import metadata
import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
import faiss
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from Helpers.user_api_key import UserAPIKey

class VectorDBHelper:
    @staticmethod
    def create_or_load_index(index_path: str, user_id: str) -> FAISS:
        user_api_key = UserAPIKey()
        choosen_llm = user_api_key.get_user_choosen_api(user_id)
        api_key = user_api_key.get_user_openai_api_key(user_id) if choosen_llm.lower() == 'openai' else os.getenv('DEFAULT_OPEN_AI_API_KEY', "")
        embedding_model = OpenAIEmbeddings(api_key=SecretStr(api_key))

        try:
            return FAISS.load_local(index_path, embedding_model, allow_dangerous_deserialization=True)

        except RuntimeError:
            index = faiss.IndexFlatL2(len(embedding_model.embed_query(index_path)))
            return FAISS(
                embedding_function=embedding_model,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={}
            )
        except Exception as e:
            raise e
        
    @staticmethod
    def add_documents_to_index(index: FAISS, documents: List[str]) -> FAISS:
        try:
            doc_objects = [Document(page_content=doc) for doc in documents]
            index.add_texts([doc.page_content for doc in doc_objects], metadatas=None)
            return index
        
        except Exception as e:
            raise e
    
    @staticmethod
    def search_index(index: FAISS, query: str, top_k=3):
        return index.similarity_search(query, top_k)