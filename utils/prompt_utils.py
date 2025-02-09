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
        retrieved_text, history_text, user_context = PromptUtil._get_prompt_utils(retrieved_docs, chat_history, user_profile)
        markdown_instructions = PromptUtil._get_markdown_instructions()

        return f"""
            {markdown_instructions}

            ## Personalization:
            - Your name is **PersonalizeGPT**.
            - You are a **helpful, personalized assistant** tailored for the user.
            - Maintain a **friendly and engaging tone**.
            - Ensure responses align with the user's personality.

            ## User Context:
            ```
            {user_context}
            ```

            ## Chat History:
            ```
            {history_text}
            ```

            ## Retrieved Context:
            ```
            {retrieved_text}
            ```

            ## Respond to the following user query in Markdown format:
            ```
            {user_input}
            ```
        """
        
    
    @staticmethod
    def generate_assistant_prompt(user_input: str, file_name: str, retrieved_docs: List[Document], chat_history: List[Any], user_profile: UserProfile) -> str: 
        retrieved_text, history_text, user_context = PromptUtil._get_prompt_utils(retrieved_docs, chat_history, user_profile)
        markdown_instructions = PromptUtil._get_markdown_instructions()

        return f"""
            {markdown_instructions}

             ## Personalization:
            - Your name is **PGPT Document Analyzer**.
            - You are a **helpful document-analyzing chatbot** designed to assist users.
            - Maintain a **friendly and engaging tone** while staying strictly within the document's knowledge.
            - You **cannot** provide answers outside the document's content.
            - If a user asks about topics not in the document, politely inform them: 
            *"I'm here to assist with analyzing the document. If your query is related to the document, I'm happy to help!"*

            ## User Context:
            ```
            {user_context}
            ```

            ## Chat History:
            ```
            {history_text}
            ```

            ## File Name:
            {file_name}

            ## Retrieved Context:
            ```
            {retrieved_text}
            ```

            ## Respond to the following user query in Markdown format:
            ```
            {user_input}
            ```
        """


    @staticmethod
    def _get_prompt_utils(retrieved_docs: List[Document], chat_history: List[Any], user_profile: UserProfile):
        retrieved_text = PromptUtil._get_formatted_retrieved_text(retrieved_docs)
        history_text = PromptUtil._get_formatted_chat_history(chat_history)
        user_context = PromptUtil.get_user_context(user_profile.to_dict())

        return retrieved_text, history_text, user_context
            
    
    @staticmethod
    def _get_formatted_chat_history(chat_history: List[Any]) -> str:
        return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
    

    @staticmethod
    def _get_formatted_retrieved_text(retrieved_docs: List[Document]) -> str:
        return "\n".join([f"- {doc.page_content}" for doc in retrieved_docs])
    

    @staticmethod
    def _get_markdown_instructions() -> str:
        return f"""
            # Instructions:
            - **Use Markdown syntax in all responses.**
            - **Ensure every response follows Markdown formatting strictly.**
            - **If a specific formatting type is needed (e.g., a list, table, or heading), ensure the response is structured accordingly.**
            - **Do NOT output plain text responses.**

            ## Markdown Formatting Guide:
            - **Headings**: Use `# H3`, `## H4`, etc. Make sure no H1.
            - Use **double newlines (`\n\n`)** before each heading (`#`, `##`, `###`, etc.) to create proper spacing.
            - Ensure that links (`[text](URL)`) appear on a new line with a blank line before them.
            - **Bold**: `**bold**`, **bold**
            - **Italic**: `*italic*`, *italic*
            - **Lists**: 
            - U
            - `- Unordered item`
            - `1. Ordered item`
            - **Code Blocks**:
            ```python
            print("Hello, World!")
            ```
            - When generating **code blocks**, follow these rules:
                1. **Specify the language** at the top in bold (e.g., `**Language: TypeScript**`).
                2. Use **triple backticks** with the language (` ```typescript `) for syntax highlighting.
                3. Wrap the code inside a `<div>` with `overflow-x: auto;` to ensure horizontal scrolling.
                4. Use **HTML `<pre>` and `<code>`** with inline CSS to apply syntax coloring for keywords.
                
            - **Tables**:
            <div style="overflow-x: auto;" class="table-container">
            ```
            | Column 1 | Column 2 |
            |----------|----------|
            | Data 1   | Data 2   |
            ```
            </div>

            - When generating **Tables**, follow these rules:
                1. Wrap the table inside a `<div>` with `overflow-x: auto;` to ensure horizontal scrolling.
        """
    

    