"""
Pytestの設定ファイル
テスト用の共通設定とフィクスチャ
"""
import pytest
import tempfile
import os
from app.app import create_app
from app.database import db


@pytest.fixture
def app():
    """テスト用のFlaskアプリケーション"""
    # 一時ファイルでテスト用データベース作成
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        
        # クリーンアップ
        db.session.remove()
        db.drop_all()
        
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """テストクライアント"""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """認証済みユーザーのヘッダー"""
    # テスト用ユーザーを登録
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password"
    }
    
    # 登録
    client.post('/api/auth/register', json=user_data)
    
    # ログイン
    login_data = {
        "username": "test_user",
        "password": "test_password"
    }
    
    response = client.post('/api/auth/login', json=login_data)
    token = response.get_json()['access_token']
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_category(client, auth_headers):
    """サンプルカテゴリ"""
    category_data = {
        "name": "テストカテゴリ",
        "color": "#ff0000",
        "description": "テスト用のカテゴリです"
    }
    
    response = client.post('/api/categories/', json=category_data, headers=auth_headers)
    return response.get_json()['category']