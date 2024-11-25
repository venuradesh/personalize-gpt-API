from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from custom_types.UserDetails import UserDetails
from models.UserModel import User
from services.user_service import UserService
from Helpers.Common import convert_json_to_user_details

user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/get_user_details', methods=['GET'])
@jwt_required(refresh=True)
def get_user_details():
    try:
        user_id = request.args.get('user_id')
        user_details = UserService().get_user_details(user_id)
        return jsonify({"message": "Successfully fetched", "data": user_details, "error": False}), 200

    except Exception as e:
        return jsonify({"message": str(e), "data": None, "error": False}), 404
    

@user_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
   
    try:
        return UserService().register_user(data)        

    except Exception as e:
        return jsonify({"message": str(e), "data": None, "error": True}), 400