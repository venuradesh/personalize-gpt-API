from datetime import datetime
from heapq import merge
from typing import List
from uuid import uuid4
from firebase_admin import firestore
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from Helpers.Common import format_date_to_gmt
from flask import session
from google.cloud import firestore as Firestore_Google

from Helpers.langchain import LangchainHelper

class ChatHistory:
    def __init__(self) -> None:
        self.db = firestore.client()
        self.CHAT_HISTORY_COLLECTION = 'pgpt-chat-history'
        self.CHAT_HISTORY_INNER_COLLECTION = 'chats'
        self.CHAT_HISTORY_INNER_DOC_COLLECTION = 'doc-chats'
        self.chat_collection = self.db.collection(self.CHAT_HISTORY_COLLECTION)

    
    def save_messages(self, user_id: str, user_msg: str, assistant_msg: str, llm) -> str:
        try: 
            if "chat_id" not in session:
                session['chat_id'] = str(uuid4())
            
            chat_id = session['chat_id']

            chat_ref = self.chat_collection.document(user_id).collection(self.CHAT_HISTORY_INNER_COLLECTION).document(chat_id)
            self._update_chat_document(chat_ref, user_msg, assistant_msg, llm)

            return chat_id

        except Exception as e:
            raise e
        
    
    def save_doc_messages(self, user_id: str, user_msg: str, assistant_msg: str, llm) -> str:
        try:
            if "doc_chat_id" not in session:
                session['doc_chat_id'] = str(uuid4())
            
            doc_chat_id = session['doc_chat_id']
            chat_ref = self.chat_collection.document(user_id).collection(self.CHAT_HISTORY_INNER_DOC_COLLECTION).document(doc_chat_id)
            self._update_chat_document(chat_ref, user_msg, assistant_msg, llm)

            return doc_chat_id

        except Exception as e:
            raise e
        

    def get_chat_history(self, user_id: str) -> List:
        try:
            if "chat_id" not in session:
                latest_chat_id = self._get_latest_chat_id(user_id)
                if latest_chat_id:
                    session['chat_id'] = latest_chat_id
                else:
                    return []
            
            chat_id = session['chat_id']
            session_data = self._get_chat_history(user_id, self.CHAT_HISTORY_INNER_COLLECTION, chat_id)
            return session_data

        except Exception as e:
            raise e
        
        
    def _get_latest_chat_id(self, user_id):
        try:
            user_chat_ref = self.chat_collection.document(user_id).collection(self.CHAT_HISTORY_INNER_COLLECTION)
            latest_chat = user_chat_ref.order_by("updated_at", direction=Firestore_Google.Query.DESCENDING).limit(1).get()

            if latest_chat:
                return latest_chat[0].id
            
            return None

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
        
    
    def _update_chat_document(self, chat_ref, user_msg: str, assistant_msg: str, llm):
        doc_snapshot = chat_ref.get()
        chat_summary = llm.predict(LangchainHelper.get_chat_summary(user_msg, assistant_msg))
        message_data = self._prepare_chat_data(user_msg, assistant_msg)
        is_new_document = not doc_snapshot.exists

        data = {
            "chat": firestore.firestore.ArrayUnion(message_data),
            "updated_at": firestore.firestore.SERVER_TIMESTAMP,  # Always update this
        }

        if is_new_document:
            data['chat_name'] = chat_summary
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
    
    def get_user_chat_history(self, user_id: str):
        try:
            collection_ref = self.chat_collection.document(user_id).collection(self.CHAT_HISTORY_INNER_COLLECTION)
            chat_docs = collection_ref.order_by("updated_at", direction=Firestore_Google.Query.DESCENDING).stream()
            
            chat_history = [ {'chat_id': doc.id, 'chat_name': doc.to_dict().get('chat_name', 'Untitled Chat')} for doc in chat_docs ]
            return chat_history

        except Exception as e:
            raise e
        
    def get_user_doc_chat_history(self, user_id: str):
        try:
            chat_docs = self.chat_collection.document(user_id).collection(self.CHAT_HISTORY_INNER_DOC_COLLECTION).stream()
            chat_history = [ {'chat_id': doc.id, 'chat_name': doc.to_dict().get('chat_name', 'Untitled Chat')} for doc in chat_docs ]
            return chat_history

        except Exception as e:
            raise e
        
    
    def is_chat_id_exists(self, user_id: str, chat_id: str) -> bool:
        try:
            chat_doc = self.chat_collection.document(user_id).collection(self.CHAT_HISTORY_INNER_COLLECTION).document(chat_id).get()
            return True if chat_doc.exists else False

        except Exception as e:
            raise e
        

    def get_chat_from_chat_id(self, user_id: str, chat_id: str):
        try:
            chat_doc = self.chat_collection.document(user_id).collection(self.CHAT_HISTORY_INNER_COLLECTION).document(chat_id).get()
            chat_dict = chat_doc.to_dict()
            
            return chat_dict.get('chat', [])
        
        except Exception as e:
            raise e
    