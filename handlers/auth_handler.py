from flask import Blueprint, jsonify, make_response, request, session
from flask_jwt_extended import jwt_required, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from services.auth_service import AuthService
from services.sendgrid_service import MailService
from services.user_service import UserService


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


@auth_blueprint.route('/forgot-password', methods=["POST"])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email', '')

        mail_service = MailService()
        mail_service.send_reset_email(email)
        return jsonify({'message': 'Succefully sent the reset instructions', 'data': None, 'error': False}), 200
    
    except Exception as e:
        return jsonify({'message': str(e), "data": None, "error": True}), 400
    


@auth_blueprint.route('/authenticate-email-by-reset-token', methods=["POST"])
def authenticate_email_by_reset_token():
    try:
        data = request.get_json()
        token = data.get('reset_token', '')

        user_service = UserService()
        user_email, user_id = user_service.get_user_email_by_refresh_token(token)

        return jsonify({'message': 'Reset token authenticated', 'data': {"email": user_email, "user_id": user_id}, 'error': False}), 200
    
    except Exception as e:
        return jsonify({'message': str(e), "data": None, "error": True}), 400
    


@auth_blueprint.route('/password-reset', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        user_id = data.get('user_id', '')
        password = data.get('password', '')
        user_service = UserService()
        user_service.reset_passwords(user_id, password)

        return jsonify({'message': 'Succefully updated the password', 'data': None, 'error': False}), 200
    
    except Exception as e:
        return jsonify({'message': str(e), "data": None, "error": True}), 400