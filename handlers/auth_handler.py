from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import jwt_required, set_access_cookies, set_refresh_cookies
from Helpers.Common import get_user_details
from custom_types.UserDetails import UserDetails
from models.UserModel import User
from services.auth_service import AuthService


auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', None)
    password = data.get('password', None)

    if not email or not password:
        return jsonify({"message": "Email and password are required.", "data": None, "error": True}), 400
    
    response, status_code = AuthService().authenticate_user(email, password)
    sending_response = {"message": response['message'], "data": response['data'], "error": response['error']}

    if status_code is 200:
        res = make_response(jsonify(sending_response), status_code)
        set_access_cookies(res, encoded_access_token=response["access_token"])
        set_refresh_cookies(res, encoded_refresh_token=response["refresh_token"])
        return res
    
    else:
        return jsonify(sending_response), status_code 



@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user_details: UserDetails = get_user_details(data)
    # New User instance
    try:
        new_user = User(user_details=user_details)
        response, status = new_user.save()

        if status is 201:
            return jsonify({"message": response['message'], "data": user_details.__dict__, "error": False}), status
        else:
            return jsonify(response), status

    except Exception as e:
        return jsonify({"message": str(e), "data": None, "error": True}), 400
