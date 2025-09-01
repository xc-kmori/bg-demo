"""
データベース設定とセットアップ
SQLite + SQLAlchemyを使用
"""
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemyインスタンス
db = SQLAlchemy()


def init_database(app):
    """データベースを初期化"""
    db.init_app(app)
    
    with app.app_context():
        # テーブル作成
        db.create_all()
        
        # 初期データの投入
        create_initial_data()


def create_initial_data():
    """初期データの作成（デモ用）"""
    from app.models import User, Category
    
    # 既にデータがある場合はスキップ
    if User.query.first():
        return
    
    # デモユーザーの作成
    demo_user = User(
        username='demo_user',
        email='demo@example.com'
    )
    demo_user.set_password('demo_password')
    db.session.add(demo_user)
    db.session.commit()
    
    # デフォルトカテゴリの作成
    default_categories = [
        Category(name='仕事', color='#007bff', description='業務関連のタスク', user_id=demo_user.id),
        Category(name='個人', color='#28a745', description='プライベートなタスク', user_id=demo_user.id),
        Category(name='勉強', color='#fd7e14', description='学習関連のタスク', user_id=demo_user.id),
        Category(name='緊急', color='#dc3545', description='緊急度の高いタスク', user_id=demo_user.id),
    ]
    
    for category in default_categories:
        db.session.add(category)
    
    db.session.commit()
    print("初期データを作成しました！")