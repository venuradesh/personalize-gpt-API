from uuid import uuid4
from flask import Blueprint, jsonify, request, session
from flask_jwt_extended import get_jwt_identity, jwt_required

from Helpers import Common
from services.chat_service import ChatService

chat_blueprint = Blueprint('chat', __name__)

@chat_blueprint.route('/query', methods=["POST"])
@jwt_required(refresh=True)
def user_query():
    user_id = get_jwt_identity()
    data = request.get_json()
    try:
        chat_service = ChatService()
        user_input = data.get('message')

        response_data = chat_service.generate_response(user_id, user_input)
        return jsonify({'message': "Response generation successfull", "data": response_data, "error": False}), 200
    
    except Exception as e:
        return jsonify({'message': str(e), "data": None, "error": True}), 400
    

@chat_blueprint.route('/load-session-chat', methods=['GET'])
@jwt_required(refresh=True)
def load_session_chat():
    try:
        user_id = get_jwt_identity()
        session_data = ChatService().load_session_chat(user_id)
        return jsonify({'message': "Session data loaded", "data": session_data, "error": False}), 200
    except Exception as e:
        return jsonify({'message': str(e), "data": None, "error": True}), 400
    

@chat_blueprint.route('/start-new-chat', methods=['GET'])
@jwt_required(refresh=True)
def start_new_chat():
    try:
        ChatService().get_new_chat()
        return jsonify({'message': 'New chat started', 'data': [], 'error': False}), 200
    except Exception as e:
        return jsonify({'message': str(e), "data": None, "error": True}), 400
    

@chat_blueprint.route('/get-chat-history', methods=['GET'])
@jwt_required(refresh=True)
def get_chat_history():
    try:
        user_id = get_jwt_identity()
        response = ChatService().get_user_chat_history(user_id)
        return jsonify({'message': 'Successfully fetched', 'data': response, 'error': False}), 200
    
    except Exception as e:
        return jsonify({'message': str(e), "data": None, "error": True}), 400
    

@chat_blueprint.route('/load-chat-from-chat-id', methods=["POST"])
@jwt_required(refresh=True)
def load_chat_from_chat_id():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        chat_id = data.get('chat_id', '')
        response = ChatService().load_chat_from_chat_id(user_id, chat_id)
        return jsonify({'message': 'Successfully loaded the chat', 'data': response, 'error': False}), 200

    except Exception as e:
        return jsonify({'message': str(e), "data": None, "error": True}), 400