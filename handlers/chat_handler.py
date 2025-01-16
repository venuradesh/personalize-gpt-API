from flask import Blueprint

from Helpers.user_api_key import UserAPIKey


chat_blueprint = Blueprint('chat', __name__)

@chat_blueprint.route('/query', methods=["POST"])
def user_query():
    user_id = 'FVP6CO0ZxmaoaJeSa6SN'
    choosen_api = UserAPIKey().get_user_llama_api_key(user_id)
    return choosen_api