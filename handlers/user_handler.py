from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from custom_types.UserDetails import UserDetails
from models.UserModel import User
from services import user_service
from services.user_service import UserService
from Helpers.Common import convert_json_to_user_details

user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/get_user_details', methods=['GET'])
@jwt_required(refresh=True)
def get_user_details():
    try:
        user_id = get_jwt_identity()
        user_details = UserService().get_user_details(user_id)
        return jsonify({"message": "Successfully fetched", "data": user_details, "error": False}), 200

    except Exception as e:
        return jsonify({"message": str(e), "data": None, "error": False}), 404
    

@user_blueprint.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        return UserService().register_user(data)        

    except Exception as e:
        return jsonify({"message": str(e), "data": None, "error": True}), 400
    

@user_blueprint.route('/update-user', methods=['PUT'])
@jwt_required(refresh=True)
def update_user(): 
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        return UserService().update_user_info(user_id=user_id, user_details=data)

    except Exception as e:
        return jsonify({"message": str(e), "data": None, "error": True}), 400
    

@user_blueprint.route('/update-llm-modal', methods=['PUT'])
@jwt_required(refresh=True)
def update_llm_modal(): 
    try:
        data = request.get_json()

        return UserService().update_llm_modal_and_keys(data)
    except Exception as e:
        return jsonify({"message": str(e), "data": None,"error": False}), 400