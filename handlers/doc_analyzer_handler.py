from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.doc_analyzer_service import DocAnalyzerService

doc_analyzer_blueprint = Blueprint('analyzer', __name__)

@doc_analyzer_blueprint.route('/upload-file', methods=['POST'])
@jwt_required(refresh=True)
def upload_file():
    try:
        if 'file' not in request.files:
            raise Exception("No file uploaded")
        
        user_id = get_jwt_identity()
        file = request.files['file']
        analyzer_service = DocAnalyzerService()
        response = analyzer_service.upload_document(user_id, file)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'message': str(e), 'data': None, 'error': True}), 400
    

@doc_analyzer_blueprint.route('/user-query', methods=['POST'])
@jwt_required(refresh=True)
def user_query():
    try:
        data = request.get_json()
        query = data.get('query', '')
        user_id = get_jwt_identity()
        analyzer_service = DocAnalyzerService()
        response = analyzer_service.generate_response(user_id, query)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'message': str(e), 'data': None, 'error': True}), 400
    