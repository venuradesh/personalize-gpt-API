from importlib import metadata
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
import faiss

class VectorDBHelper:
    @staticmethod
    def create_or_load_index(index_path: str):
        try:
            return FAISS.load_local(index_path, OpenAIEmbeddings())
        except FileNotFoundError:
            index = faiss.IndexFlatL2(len(OpenAIEmbeddings().embed_query(index_path)))
            return FAISS(
                embedding_function=OpenAIEmbeddings(),
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