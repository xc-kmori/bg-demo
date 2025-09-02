"""
Flaskアプリケーションファクトリ
メインアプリケーションの設定とルート定義
"""
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import config
from app.database import db, init_database


def create_app(config_name='development'):
    """Flaskアプリケーションファクトリ"""
    app = Flask(__name__)
    
    # 設定読み込み
    app.config.from_object(config[config_name])
    
    # JWT設定
    jwt = JWTManager(app)
    
    # CORS設定（フロントエンドからのアクセスを許可）
    CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080", "file://"])
    
    # データベース初期化
    init_database(app)
    
    # エラーハンドラー
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'リソースが見つかりません'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'サーバー内部エラーが発生しました'}), 500
    
    # ヘルスチェックエンドポイント
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'OK',
            'message': 'タスク管理API は正常に動作中です',
            'version': '1.0.0'
        })
    
    # ルート登録
    register_blueprints(app)
    
    return app


def register_blueprints(app):
    """ブループリントの登録"""
    from app.routers.auth import auth_bp
    from app.routers.tasks import tasks_bp
    from app.routers.categories import categories_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')