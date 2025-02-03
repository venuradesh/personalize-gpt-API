from flask import Blueprint, jsonify, request

from services.doc_analyzer_service import DocAnalyzerService

doc_analyzer_blueprint = Blueprint('analyzer', __name__)

@doc_analyzer_blueprint.route('/upload-file', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            raise Exception("No file uploaded")
        
        user_id = "FVP6CO0ZxmaoaJeSa6SN"
        file = request.files['file']
        analyzer_service = DocAnalyzerService()
        response = analyzer_service.upload_document(user_id, file)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'message': str(e), 'data': None, 'error': True}), 400
    

@doc_analyzer_blueprint.route('/user-query', methods=['POST'])
def user_query():
    try:
        data = request.get_json()
        query = data.get('query', '')
        user_id = "FVP6CO0ZxmaoaJeSa6SN"
        analyzer_service = DocAnalyzerService()
        response = analyzer_service.generate_response(user_id, query)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'message': str(e), 'data': None, 'error': True}), 400
    