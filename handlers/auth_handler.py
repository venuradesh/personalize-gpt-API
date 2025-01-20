from flask import Blueprint, jsonify, make_response, request, session
from flask_jwt_extended import jwt_required, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
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

    if status_code == 200:
        res = make_response(jsonify(sending_response), status_code)

        set_access_cookies(res, response["access_token"])
        set_refresh_cookies(res, response["refresh_token"])
        res.set_cookie('access_token', value=response["access_token"], httponly=False, secure=False, samesite=None, path='/')
        return res
    
    else:
        return jsonify(sending_response), status_code 
    

@auth_blueprint.route('/logout', methods=['POST'])
@jwt_required(optional=True)
def logout():
    response = jsonify({'message': 'Logout successful', 'data': None, 'error': False})
    unset_jwt_cookies(response)
    session.clear()

    return response, 200