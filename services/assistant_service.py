import os
from typing import Dict, List
from flask import session
import openai
from pydantic import SecretStr


class AssistantService:
    def __init__(self) -> None:
        pass

    @staticmethod
    def upload_file_to_openai(file, api_key: str) -> str:
        try:
            openai.api_key = api_key
            file_extension = os.path.splitext(file.filename)[-1].lower().lstrip('.')

            if file_extension != 'pdf':
                raise ValueError("Only PDFs are allowed for the moment")

            uploaded_file_name = session.get('uploaded_file_name', '')
            if uploaded_file_name == file.filename:
                return session['file_id']
            
            with file.stream as uploaded_file:
                message_file = openai.files.create(file=(file.filename, uploaded_file, 'application/pdf'), purpose='assistants')

            session['file_id'] = message_file.id
            session['uploaded_file_name'] = file.filename
            session['file_extension'] = file_extension

            return message_file.id
        
        except Exception as e:
            raise e
        

    @staticmethod
    def process_query(query: str, user_id: str, api_key: str, chat_history: List = []):
        try:
            file_id = session['file_id'] 
            if not file_id:
                raise ValueError("No file has been uploaded")
            
            thread_id = session['openai_thread_id']
            if not thread_id:
                thread = openai.beta.threads.create()
                thread_id = thread.id
                session['openai_thread_id'] = thread_id

            # TODO: Include chat history

            formatted_chat_history = AssistantService.get_formatted_chat_history_for_openai_assistant(chat_history)

            openai.beta.threads.messages.create(
                thread_id=thread_id,
                role='user',
                content=query,
                attachments=[
                    {'file_id': file_id, 'tools': [{'type': 'file_search'}]}
                ]
            )

            assistant_id = AssistantService.create_openai_assistant(api_key)
            run = openai.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=assistant_id,
                instructions=f"Use this chat history to answer the given questions. {formatted_chat_history}. \n"
            )

            while run.status in ["queued", "in_progress"]:
                run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

            messages = openai.beta.threads.messages.list(thread_id=thread_id)
            assistant_response = ''.join(block.text.value for block in messages.data[0].content if block.type == 'text')

            return assistant_response

        except Exception as e:
            raise Exception(f"Error in OpenAI Assistant response: {str(e)}")

    @staticmethod
    def create_openai_assistant(api_key: str) -> str:
        try:
            openai.api_key = api_key
            assistant_id = session.get('assistant_id', '')

            if assistant_id:
                return assistant_id
            
            assistant = openai.beta.assistants.create(
                name='Document Analyzer',
                instructions='You are a document analysis assistant. Answer questions based on uploaded documents.',
                tools=[{'type': 'file_search'}],
                model='gpt-4-turbo'
            )

            session['assistant_id'] = assistant.id
            return assistant.id

        except Exception as e:
            raise e
        

    @staticmethod
    def get_formatted_chat_history_for_openai_assistant(chat_history: List) -> str:
        return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])