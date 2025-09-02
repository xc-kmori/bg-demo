"""
API動作確認用テストスクリプト
基本的なエンドポイントの動作をテスト
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5001"

def test_health_check():
    """ヘルスチェック"""
    print("=== ヘルスチェック ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"ステータス: {response.status_code}")
        print(f"レスポンス: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"エラー: {e}")
        return False

def test_user_registration():
    """ユーザー登録テスト"""
    print("\n=== ユーザー登録 ===")
    user_data = {
        "username": "test_user",
        "email": "test@example.com", 
        "password": "test_password"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        print(f"ステータス: {response.status_code}")
        print(f"レスポンス: {response.json()}")
        return response.status_code in [201, 409]  # 201=新規作成, 409=既存ユーザー
    except Exception as e:
        print(f"エラー: {e}")
        return False

def test_user_login():
    """ユーザーログインテスト"""
    print("\n=== ユーザーログイン ===")
    login_data = {
        "username": "test_user",
        "password": "test_password"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"ステータス: {response.status_code}")
        data = response.json()
        print(f"レスポンス: {data}")
        
        if response.status_code == 200:
            return data.get('access_token')
        return None
    except Exception as e:
        print(f"エラー: {e}")
        return None

def test_create_task(token):
    """タスク作成テスト"""
    print("\n=== タスク作成 ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    task_data = {
        "title": "Background Agentテスト用タスク",
        "description": "このタスクはBackground Agentによって自動作成されました",
        "priority": "high",
        "due_date": (datetime.now() + timedelta(days=3)).isoformat()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/tasks/", json=task_data, headers=headers)
        print(f"ステータス: {response.status_code}")
        print(f"レスポンス: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"エラー: {e}")
        return False

def test_get_tasks(token):
    """タスク一覧取得テスト"""
    print("\n=== タスク一覧取得 ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
        print(f"ステータス: {response.status_code}")
        data = response.json()
        print(f"タスク数: {data.get('total', 0)}")
        
        if data.get('tasks'):
            for task in data['tasks'][:3]:  # 最初の3件を表示
                print(f"  - {task['title']} ({task['status']})")
                
        return response.status_code == 200
    except Exception as e:
        print(f"エラー: {e}")
        return False

def run_tests():
    """全テストの実行"""
    print("🚀 タスク管理API 動作確認開始\n")
    
    # ヘルスチェック
    if not test_health_check():
        print("❌ サーバーが起動していません")
        return
    
    # ユーザー登録
    test_user_registration()
    
    # ログイン
    token = test_user_login()
    if not token:
        print("❌ ログインに失敗しました")
        return
    
    # タスク操作
    test_create_task(token)
    test_get_tasks(token)
    
    print("\n✅ 基本的なAPI動作確認が完了しました！")

if __name__ == "__main__":
    run_tests()