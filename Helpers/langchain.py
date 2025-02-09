import os
from flask import session
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.schema import Document, BaseRetriever
from Helpers.vector_db import VectorDBHelper
from typing import List
from pydantic import SecretStr
from custom_types.UserDetails import UserProfile
from utils.prompt_utils import PromptUtil
from langchain.tools import Tool
from langchain_community.utilities import SerpAPIWrapper, WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper, OpenWeatherMapAPIWrapper
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
import wikipediaapi

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
    def initialize_agent(api_key:str, choosen_llm: str):
        try:
            langchain_helper = LangchainHelper()
            llm = LangchainHelper.initialize_llm(choosen_llm, api_key)
            wikipedia_tool = langchain_helper._get_wikipedia_tool()
            serp_tool = langchain_helper._get_serp_api_tool()
            duck_duck_go_tool = langchain_helper._get_duckduckgo_tool()
            whether_tool = langchain_helper._get_whether_tool()

            memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
            agent = initialize_agent(
                tools=[whether_tool, duck_duck_go_tool, serp_tool, wikipedia_tool],
                llm=llm,
                agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                memory=memory
            )
            return agent

        except Exception as e:
            raise e


    @staticmethod
    def create_retriever(user_id, vector_db_path: str, top_k: int = 3) -> BaseRetriever:
        index = VectorDBHelper.create_or_load_index(vector_db_path, user_id)
        return index.as_retriever(search_kwargs={"k": top_k})
    
    @staticmethod
    def generate_prompt(user_input: str, retrieved_docs: List[Document], chat_history: List[str], user_profile: UserProfile) -> str:
        return PromptUtil.generate_prompt(user_input, retrieved_docs, chat_history, user_profile)
    

    @staticmethod
    def generate_doc_prompt(user_input: str, retreved_docs: List[Document], chat_history: List[str], user_profile: UserProfile) -> str:
        file_name = session.get('file_name', '')
        return PromptUtil.generate_assistant_prompt(user_input, file_name, retreved_docs, chat_history, user_profile)
    

    def _get_wikipedia_tool(self):
        contact_email = os.getenv('CONTACT_EMAIL')
        wikipedia_client = wikipediaapi.Wikipedia(user_agent=f"PersonalizeGPT/1.0 (contact: {contact_email})")
        return Tool(
            name='Wikipedia',
            func=WikipediaAPIWrapper(wiki_client=wikipedia_client).run,
            description="Use this tool to search Wikipedia for structured and accurate information."
        )
    

    def _get_duckduckgo_tool(self):
        return Tool(
            name="DuckDuckGo Search",
            func=DuckDuckGoSearchAPIWrapper().run,
            description="Use this tool to fetch real-time information from the internet using DuckDuckGo."
        )


    def _get_serp_api_tool(self):
        serp_api_key = os.getenv('SERPAPI_API_KEY')
        return Tool(
            name='Google Search',
            func=SerpAPIWrapper(serpapi_api_key=serp_api_key).run,
            description="Use this tool for fetching real-time information from the internet."
        )
    

    def _get_whether_tool(self):
        return Tool(
            name="Wheather Lookup",
            func=OpenWeatherMapAPIWrapper().run,
            description="Use this tool to get real-time weather information for a given location."
        )


