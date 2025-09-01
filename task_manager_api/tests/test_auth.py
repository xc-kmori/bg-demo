"""
認証機能のテスト
ユーザー登録、ログイン、トークン管理のテスト
"""
import pytest


class TestAuth:
    """認証機能のテストクラス"""

    def test_user_registration_success(self, client):
        """正常なユーザー登録"""
        user_data = {
            "username": "new_user",
            "email": "new_user@example.com",
            "password": "secure_password"
        }
        
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['message'] == 'ユーザー登録が完了しました'
        assert data['user']['username'] == 'new_user'
        assert 'password' not in data['user']  # パスワードは返さない

    def test_user_registration_duplicate_username(self, client):
        """重複ユーザー名での登録エラー"""
        user_data = {
            "username": "duplicate_user",
            "email": "user1@example.com",
            "password": "password"
        }
        
        # 1回目の登録
        client.post('/api/auth/register', json=user_data)
        
        # 2回目の登録（重複）
        user_data['email'] = 'user2@example.com'  # メールは変更
        response = client.post('/api/auth/register', json=user_data)
        
        assert response.status_code == 409
        assert 'このユーザー名は既に使用されています' in response.get_json()['error']

    def test_user_registration_missing_fields(self, client):
        """必須フィールドが不足した場合"""
        # ユーザー名なし
        response = client.post('/api/auth/register', json={
            "email": "test@example.com",
            "password": "password"
        })
        assert response.status_code == 400
        
        # パスワードなし
        response = client.post('/api/auth/register', json={
            "username": "testuser",
            "email": "test@example.com"
        })
        assert response.status_code == 400

    def test_login_success(self, client):
        """正常なログイン"""
        # ユーザー登録
        user_data = {
            "username": "login_user",
            "email": "login@example.com",
            "password": "login_password"
        }
        client.post('/api/auth/register', json=user_data)
        
        # ログイン
        login_data = {
            "username": "login_user",
            "password": "login_password"
        }
        
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['username'] == 'login_user'

    def test_login_wrong_credentials(self, client):
        """間違った認証情報でのログイン"""
        # 存在しないユーザー
        response = client.post('/api/auth/login', json={
            "username": "nonexistent",
            "password": "password"
        })
        assert response.status_code == 401
        
        # 間違ったパスワード
        user_data = {
            "username": "test_wrong_pass",
            "email": "test@example.com",
            "password": "correct_password"
        }
        client.post('/api/auth/register', json=user_data)
        
        response = client.post('/api/auth/login', json={
            "username": "test_wrong_pass",
            "password": "wrong_password"
        })
        assert response.status_code == 401

    def test_get_current_user(self, client, auth_headers):
        """認証済みユーザー情報取得"""
        response = client.get('/api/auth/me', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'test_user'