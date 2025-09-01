"""
認証関連のAPIエンドポイント
ユーザー登録、ログイン、トークン管理
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models import User
from app.database import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """ユーザー登録"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSONデータが必要です'}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'ユーザー名、メールアドレス、パスワードは必須項目です'}), 400
            
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
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'登録処理でエラーが発生しました: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """ユーザーログイン"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSONデータが必要です'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'ユーザー名とパスワードは必須項目です'}), 400
            
        # ユーザー認証
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'ユーザー名またはパスワードが正しくありません'}), 401
            
        if not user.is_active:
            return jsonify({'error': 'アカウントが無効になっています'}), 401
            
        # トークン生成
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'ログインに成功しました',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'ログイン処理でエラーが発生しました: {str(e)}'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """アクセストークン更新"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'ユーザーが見つからないか無効です'}), 401
            
        new_token = create_access_token(identity=current_user_id)
        return jsonify({
            'message': 'トークンを更新しました',
            'access_token': new_token
        })
        
    except Exception as e:
        return jsonify({'error': f'トークン更新でエラーが発生しました: {str(e)}'}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """現在のユーザー情報取得"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'ユーザーが見つかりません'}), 404
            
        return jsonify({
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'ユーザー情報取得でエラーが発生しました: {str(e)}'}), 500