from uuid import uuid4
from flask import Blueprint, jsonify, request, session

from Helpers import Common
from services.chat_service import ChatService

chat_blueprint = Blueprint('chat', __name__)

@chat_blueprint.route('/query', methods=["POST"])
def user_query():
    user_id = 'FVP6CO0ZxmaoaJeSa6SN'
    data = request.get_json()
    try:
        chat_service = ChatService()
        user_input = data.get('message')

        response_data = chat_service.generate_response(user_id, user_input)
        return jsonify({'message': "Response generation successfull", "data": response_data, "error": False}), 200
    
    except Exception as e:
        return jsonify({'message': str(e), "data": None, "error": True}), 400