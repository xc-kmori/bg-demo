"""
認証関連のAPIエンドポイント
ユーザー登録、ログイン、トークン管理
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models import User
from app.database import db
from app.utils.validators import UserValidator, ValidationError
from app.utils.decorators import combined_decorator, handle_errors

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@combined_decorator
def register():
    """ユーザー登録"""
    data = request.get_json()
    
    # バリデーション実行
    validated_data = UserValidator.validate_user_registration(data)
    username = validated_data['username']
    email = validated_data['email']
    password = validated_data['password']
    
    # 既存ユーザーチェック
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'このユーザー名は既に使用されています'}), 409
        
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'このメールアドレスは既に登録されています'}), 409
        
    # 新規ユーザー作成
    user = User(username=username, email=email)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'ユーザー登録が完了しました',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
@combined_decorator
def login():
    """ユーザーログイン"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        raise ValidationError('ユーザー名とパスワードは必須項目です')
    
    # ユーザー認証
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'ユーザー名またはパスワードが正しくありません'}), 401
        
    if not user.is_active:
        return jsonify({'error': 'アカウントが無効になっています'}), 401
        
    # トークン生成
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'ログインに成功しました',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    })


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@handle_errors
def refresh():
    """アクセストークン更新"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'error': 'ユーザーが見つからないか無効です'}), 401
        
    new_token = create_access_token(identity=str(current_user_id))
    return jsonify({
        'message': 'トークンを更新しました',
        'access_token': new_token
    })


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
@handle_errors
def get_current_user():
    """現在のユーザー情報取得"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'ユーザーが見つかりません'}), 404
        
    return jsonify({
        'user': user.to_dict()
    })