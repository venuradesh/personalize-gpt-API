from datetime import datetime
from heapq import merge
from typing import List
from uuid import uuid4
from firebase_admin import firestore
from Helpers.Common import format_date_to_gmt
from flask import session

class ChatHistory:
    def __init__(self) -> None:
        self.db = firestore.client()
        self.CHAT_HISTORY_COLLECTION = 'pgpt-chat-history'
        self.CHAT_HISTORY_INNER_COLLECTION = 'chats'
        self.chat_collection = self.db.collection(self.CHAT_HISTORY_COLLECTION)

    
    def save_messages(self, user_id: str, user_msg: str, assistant_msg: str) -> str:
        try: 
            if "chat_id" not in session:
                session['chat_id'] = str(uuid4())
            
            chat_id = session['chat_id']

            chat_ref = self.chat_collection.document(user_id).collection(self.CHAT_HISTORY_INNER_COLLECTION).document(chat_id)
            message_data = self._prepare_chat_data(user_msg, assistant_msg)
            doc_snapshot = chat_ref.get()
            is_new_document = not doc_snapshot.exists

            #save or update the chat document
            data = {
                "chat": firestore.firestore.ArrayUnion(message_data),
                "updated_at": firestore.firestore.SERVER_TIMESTAMP,  # Always update this
            }

            if is_new_document:
                data["created_at"] = firestore.firestore.SERVER_TIMESTAMP 

            chat_ref.set(data, merge=True)

            return chat_id

        except Exception as e:
            raise e
        

    def get_chat_history(self, user_id: str) -> List:
        try:
            if "chat_id" not in session:
                return []
            
            chat_id = session['chat_id']

            chat_ref = self.chat_collection.document(user_id).collection(self.CHAT_HISTORY_INNER_COLLECTION).document(chat_id)
            chat_doc = chat_ref.get()

            if not chat_doc.exists:
                return []
            
            return chat_doc.to_dict().get('chat', [])

        except Exception as e:
            raise e


        
    def _prepare_chat_data(self, user_msg: str, assistant_msg: str) -> List:
        return [
            {
                "role": "user",
                "content": user_msg,
                "timestamp": format_date_to_gmt()
            },
            {
                "role": "assistant",
                "content": assistant_msg,
                "timestamp": format_date_to_gmt()
            }
        ]