"""
カテゴリ機能のテスト
カテゴリのCRUD操作のテスト
"""
import pytest


class TestCategories:
    """カテゴリ機能のテストクラス"""

    def test_create_category_success(self, client, auth_headers):
        """カテゴリ作成の正常ケース"""
        category_data = {
            "name": "新しいカテゴリ",
            "color": "#00ff00",
            "description": "新規カテゴリの説明"
        }
        
        response = client.post('/api/categories/', json=category_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['message'] == 'カテゴリを作成しました'
        assert data['category']['name'] == '新しいカテゴリ'
        assert data['category']['color'] == '#00ff00'

    def test_create_category_missing_name(self, client, auth_headers):
        """カテゴリ名なしでの作成エラー"""
        category_data = {
            "color": "#ff0000",
            "description": "名前がないカテゴリ"
        }
        
        response = client.post('/api/categories/', json=category_data, headers=auth_headers)
        assert response.status_code == 400
        assert 'カテゴリ名は必須項目です' in response.get_json()['error']

    def test_create_category_duplicate_name(self, client, auth_headers):
        """重複カテゴリ名での作成エラー"""
        category_data = {
            "name": "重複テスト",
            "color": "#ff0000"
        }
        
        # 1回目の作成
        client.post('/api/categories/', json=category_data, headers=auth_headers)
        
        # 2回目の作成（重複）
        response = client.post('/api/categories/', json=category_data, headers=auth_headers)
        assert response.status_code == 409
        assert 'このカテゴリ名は既に存在します' in response.get_json()['error']

    def test_get_categories(self, client, auth_headers):
        """カテゴリ一覧取得"""
        # カテゴリを作成
        categories = [
            {"name": "カテゴリA", "color": "#ff0000"},
            {"name": "カテゴリB", "color": "#00ff00"},
            {"name": "カテゴリC", "color": "#0000ff"}
        ]
        
        for category_data in categories:
            client.post('/api/categories/', json=category_data, headers=auth_headers)
        
        response = client.get('/api/categories/', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['categories']) >= 3  # 初期データも含む

    def test_update_category_success(self, client, auth_headers, sample_category):
        """カテゴリ更新の正常ケース"""
        category_id = sample_category['id']
        
        update_data = {
            "name": "更新されたカテゴリ",
            "color": "#purple",
            "description": "更新されたカテゴリの説明"
        }
        
        response = client.put(f'/api/categories/{category_id}', json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['category']['name'] == '更新されたカテゴリ'
        assert data['category']['color'] == '#purple'

    def test_delete_category_success(self, client, auth_headers):
        """カテゴリ削除の正常ケース（タスクなし）"""
        # 空のカテゴリを作成
        category_data = {"name": "削除予定カテゴリ"}
        response = client.post('/api/categories/', json=category_data, headers=auth_headers)
        category_id = response.get_json()['category']['id']
        
        # カテゴリを削除
        response = client.delete(f'/api/categories/{category_id}', headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()['message'] == 'カテゴリを削除しました'

    def test_delete_category_with_tasks(self, client, auth_headers, sample_category):
        """タスクありカテゴリの削除エラー"""
        category_id = sample_category['id']
        
        # カテゴリにタスクを作成
        task_data = {
            "title": "カテゴリ紐づけタスク",
            "category_id": category_id
        }
        client.post('/api/tasks/', json=task_data, headers=auth_headers)
        
        # カテゴリ削除を試行
        response = client.delete(f'/api/categories/{category_id}', headers=auth_headers)
        assert response.status_code == 409
        assert 'タスクが存在するため削除できません' in response.get_json()['error']

    def test_get_category_tasks(self, client, auth_headers, sample_category):
        """特定カテゴリのタスク一覧取得"""
        category_id = sample_category['id']
        
        # カテゴリにタスクを複数作成
        tasks = [
            {"title": "カテゴリタスク1", "category_id": category_id},
            {"title": "カテゴリタスク2", "category_id": category_id}
        ]
        
        for task_data in tasks:
            client.post('/api/tasks/', json=task_data, headers=auth_headers)
        
        # カテゴリのタスク取得
        response = client.get(f'/api/categories/{category_id}/tasks', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['category']['id'] == category_id
        assert len(data['tasks']) == 2
        assert all(task['category_id'] == category_id for task in data['tasks'])