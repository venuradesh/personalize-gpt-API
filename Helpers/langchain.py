from langchain.chat_models import openai
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.schema import Document, BaseRetriever
from Helpers.vector_db import VectorDBHelper
from typing import List
from pydantic import SecretStr

class LangchainHelper:
    @staticmethod
    def initialize_llm(choosen_llm: str, api_key: str, temperature: float = 0.6):
        try:
            if choosen_llm.lower() == 'openai':
                return ChatOpenAI(
                    model='gpt-4o-mini',
                    api_key=SecretStr(api_key),
                    temperature=temperature
                )
            elif choosen_llm.lower() == 'llama-3.1':
                return ChatGroq(
                    model="llama-3.3-70b-versatile",
                    temperature=temperature,
                    api_key=SecretStr(api_key)
                )
            else:
                raise ValueError('Invalid LLM')

        except Exception as e:
            raise e

    @staticmethod
    def create_retriever(vector_db_path: str, top_k: int = 3) -> BaseRetriever:
        index = VectorDBHelper.create_or_load_index(vector_db_path)
        return index.as_retriever(search_kwargs={"k": top_k})
    
    # @staticmethod
    # def generate_prompt(user_input: str, retrieved_docs: List[Document], chat_history: List[str]) -> str:
    #     retrieved_text = "\n".join([f"- {doc.page_content}" for doc in retrieved_docs])
    #     history_text = "\n".join(chat_history)

