import os
from typing import Dict, List
from flask import session
import openai
from pydantic import SecretStr
import requests


class AssistantService:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_assistant_and_tool(file_extension: str):
        assistants_and_tools = {
            'pdf': ("asst_fZkHJmy8MTZew183ecI8H5yf", "file_search"),

            # TODO: Enable the other file formats later
            # "doc": ("asst_kdI13H9SJcyAuYP4CIYKAm70", "file_search"),
            # "docx": ("asst_kdI13H9SJcyAuYP4CIYKAm70", "file_search"),
            # "txt": ("asst_dtuMqbYp8NoTqmjcSIoR9HZb", "file_search"),
            # "csv": ("asst_dAvw9gE2NcDA9q8wJYQkbpuH", "code_interpreter"),
            # "xlsx": ("asst_0mBnRhStoBOz6XbHx4ots6bL", "code_interpreter")
        }

        return assistants_and_tools.get(file_extension, ("asst_fZkHJmy8MTZew183ecI8H5yf", "file_search"))
    
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
            
            file_extension = session.get('file_extension', 'pdf')
            assistant_id, tool_type = AssistantService.get_assistant_and_tool(file_extension)

            thread_id = session['openai_thread_id']
            if not thread_id:
                thread = openai.beta.threads.create()
                thread_id = thread.id
                session['openai_thread_id'] = thread_id

            # TODO: Include chat history

            openai.beta.threads.messages.create(
                thread_id=thread_id,
                role='user',
                content=query,
                attachments=[
                    {'file_id': file_id}
                ]
            )

            run = openai.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
            )

            while run.status in ["queued", "in_progress"]:
                run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

            messages = openai.beta.threads.messages.list(thread_id=thread_id)
            assistant_response = messages.data[0].content

            return {'message': 'Query processed', 'data': assistant_response, 'error': False}

        except Exception as e:
            raise Exception(f"Error in OpenAI Assistant response: {str(e)}")


