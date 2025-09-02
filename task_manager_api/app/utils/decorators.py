"""
デコレータ関数
エラーハンドリング、ログ機能など
"""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.utils.logger import logger
from app.utils.validators import ValidationError


def handle_errors(f):
    """エラーハンドリングデコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.log_api_error(request.endpoint, f"Validation error: {e.message}")
            return jsonify({'error': e.message}), 400
        except Exception as e:
            logger.log_api_error(request.endpoint, f"Unexpected error: {str(e)}")
            return jsonify({'error': 'サーバー内部エラーが発生しました'}), 500
    return decorated_function


def log_request(f):
    """リクエストログデコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = None
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except:
            pass  # トークンがない場合は無視
        
        logger.log_api_request(request.endpoint, request.method, user_id)
        return f(*args, **kwargs)
    return decorated_function


def validate_json(f):
    """JSON形式チェックデコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT'] and not request.is_json:
            return jsonify({'error': 'Content-Type: application/json が必要です'}), 400
        return f(*args, **kwargs)
    return decorated_function


def combined_decorator(f):
    """複合デコレータ（ログ、エラーハンドリング、JSON検証）"""
    return handle_errors(log_request(validate_json(f)))