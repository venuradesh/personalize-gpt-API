from typing import Any, List
from langchain.schema import Document

from custom_types.UserDetails import UserProfile

class PromptUtil:
    @staticmethod
    def get_user_context(user_profile: dict) -> str:
        first_name = user_profile.get("first_name", "User")
        last_name = user_profile.get("last_name", "")
        job_title = user_profile.get("job_title", "individual")
        personality = user_profile.get("personality", "neutral")
        description = user_profile.get("description", "")
        country = user_profile.get("country", "")
        
        # Prepare user-specific context
        return f"""
        User Profile:
        - Full Name: {first_name} {last_name}
        - Calling Name: {first_name}
        - Job Title: {job_title}
        - Personality: {personality}
        - Description: {description}
        - Country: {country}
        """

    @staticmethod
    def generate_prompt(user_input: str, retrieved_docs: List[Document], chat_history: List[Any], user_profile: UserProfile):
        retrieved_text = "\n".join([f"- {doc.page_content}" for doc in retrieved_docs])
        history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
        user_context = PromptUtil.get_user_context(user_profile.to_dict())

        return f"""
            Your name is PersonalizeGPT.\
            You are a helpful assistant personalized for the user to cater the answers that the user is expecting.\
            Use the following details to tailor your responses:

            {user_context}

            Chat History: 
            {history_text}

            Based on the following retrieved context:
            {retrieved_text}

            Respond to the user query:
            {user_input}
        """
    

    