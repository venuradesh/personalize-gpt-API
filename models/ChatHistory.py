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
        self.CHAT_HISTORY_INNER_DOC_COLLECTION = 'doc-chats'
        self.chat_collection = self.db.collection(self.CHAT_HISTORY_COLLECTION)

    
    def save_messages(self, user_id: str, user_msg: str, assistant_msg: str) -> str:
        try: 
            if "chat_id" not in session:
                session['chat_id'] = str(uuid4())
            
            chat_id = session['chat_id']

            chat_ref = self.chat_collection.document(user_id).collection(self.CHAT_HISTORY_INNER_COLLECTION).document(chat_id)
            self._update_chat_document(chat_ref, user_msg, assistant_msg)

            return chat_id

        except Exception as e:
            raise e
        
    
    def save_doc_messages(self, user_id: str, user_msg: str, assistant_msg: str) -> str:
        try:
            if "doc_chat_id" not in session:
                session['doc_chat_id'] = str(uuid4())
            
            doc_chat_id = session['doc_chat_id']
            chat_ref = self.chat_collection.document(user_id).collection(self.CHAT_HISTORY_INNER_DOC_COLLECTION).document(doc_chat_id)
            self._update_chat_document(chat_ref, user_msg, assistant_msg)

            return doc_chat_id

        except Exception as e:
            raise e
        

    def get_chat_history(self, user_id: str) -> List:
        try:
            if "chat_id" not in session:
                return []
            
            chat_id = session['chat_id']
            return self._get_chat_history(user_id, self.CHAT_HISTORY_INNER_COLLECTION, chat_id)

        except Exception as e:
            raise e
        
    def get_doc_chat_history(self, user_id) -> List:
        if "doc_chat_id" not in session:
                session['doc_chat_id'] = str(uuid4())
            
        doc_chat_id = session['doc_chat_id']
        return self._get_chat_history(user_id, self.CHAT_HISTORY_INNER_DOC_COLLECTION, doc_chat_id)
        
    

    def _get_chat_history(self, user_id: str, colelction_name: str, chat_id: str) -> List:
        try:
            chat_ref = self.chat_collection.document(user_id).collection(colelction_name).document(chat_id)
            chat_doc = chat_ref.get()

            if not chat_doc.exists:
                return []
            
            return chat_doc.to_dict().get('chat', [])

        except Exception as e:
            raise e


    def _update_chat_document(self, chat_ref, user_msg: str, assistant_msg: str):
        doc_snapshot = chat_ref.get()
        message_data = self._prepare_chat_data(user_msg, assistant_msg)
        is_new_document = not doc_snapshot.exists

        data = {
            "chat": firestore.firestore.ArrayUnion(message_data),
            "updated_at": firestore.firestore.SERVER_TIMESTAMP,  # Always update this
        }

        if is_new_document:
            data["created_at"] = firestore.firestore.SERVER_TIMESTAMP 

        chat_ref.set(data, merge=True)

        
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