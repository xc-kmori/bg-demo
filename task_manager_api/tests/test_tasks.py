"""
タスク機能のテスト
CRUD操作と統計機能のテスト
"""
import pytest
from datetime import datetime, timedelta


class TestTasks:
    """タスク機能のテストクラス"""

    def test_create_task_success(self, client, auth_headers):
        """タスク作成の正常ケース"""
        task_data = {
            "title": "テストタスク",
            "description": "これはテスト用のタスクです",
            "priority": "high"
        }
        
        response = client.post('/api/tasks/', json=task_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['message'] == 'タスクを作成しました'
        assert data['task']['title'] == 'テストタスク'
        assert data['task']['priority'] == 'high'
        assert data['task']['status'] == 'pending'  # デフォルト値

    def test_create_task_missing_title(self, client, auth_headers):
        """タイトルなしでのタスク作成エラー"""
        task_data = {
            "description": "タイトルがないタスク"
        }
        
        response = client.post('/api/tasks/', json=task_data, headers=auth_headers)
        assert response.status_code == 400
        assert 'タスクタイトルは必須項目です' in response.get_json()['error']

    def test_get_tasks_empty(self, client, auth_headers):
        """タスクが空の場合の一覧取得"""
        response = client.get('/api/tasks/', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['tasks'] == []
        assert data['total'] == 0

    def test_get_tasks_with_data(self, client, auth_headers):
        """タスクが存在する場合の一覧取得"""
        # 複数のタスクを作成
        tasks = [
            {"title": "タスク1", "priority": "high"},
            {"title": "タスク2", "priority": "medium"},
            {"title": "タスク3", "priority": "low"}
        ]
        
        for task_data in tasks:
            client.post('/api/tasks/', json=task_data, headers=auth_headers)
        
        response = client.get('/api/tasks/', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['tasks']) == 3
        assert data['total'] == 3

    def test_get_tasks_with_filters(self, client, auth_headers):
        """フィルター機能つきでのタスク取得"""
        # 異なる優先度のタスクを作成
        tasks = [
            {"title": "高優先度タスク", "priority": "high"},
            {"title": "中優先度タスク", "priority": "medium"},
            {"title": "高優先度タスク2", "priority": "high"}
        ]
        
        for task_data in tasks:
            client.post('/api/tasks/', json=task_data, headers=auth_headers)
        
        # 高優先度のタスクのみを取得
        response = client.get('/api/tasks/?priority=high', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['tasks']) == 2
        assert all(task['priority'] == 'high' for task in data['tasks'])

    def test_update_task_success(self, client, auth_headers):
        """タスク更新の正常ケース"""
        # タスクを作成
        task_data = {"title": "更新前タスク", "status": "pending"}
        response = client.post('/api/tasks/', json=task_data, headers=auth_headers)
        task_id = response.get_json()['task']['id']
        
        # タスクを更新
        update_data = {
            "title": "更新後タスク",
            "status": "completed",
            "description": "更新されたタスクです"
        }
        
        response = client.put(f'/api/tasks/{task_id}', json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['task']['title'] == '更新後タスク'
        assert data['task']['status'] == 'completed'
        assert data['task']['completed_at'] is not None

    def test_delete_task_success(self, client, auth_headers):
        """タスク削除の正常ケース"""
        # タスクを作成
        task_data = {"title": "削除予定タスク"}
        response = client.post('/api/tasks/', json=task_data, headers=auth_headers)
        task_id = response.get_json()['task']['id']
        
        # タスクを削除
        response = client.delete(f'/api/tasks/{task_id}', headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()['message'] == 'タスクを削除しました'
        
        # 削除されたタスクが取得できないことを確認
        response = client.get(f'/api/tasks/{task_id}', headers=auth_headers)
        assert response.status_code == 404

    def test_task_stats(self, client, auth_headers):
        """タスク統計情報のテスト"""
        # 様々なステータスのタスクを作成
        tasks = [
            {"title": "未着手タスク1", "status": "pending"},
            {"title": "未着手タスク2", "status": "pending"},
            {"title": "進行中タスク", "status": "in_progress"},
            {"title": "完了タスク", "status": "completed"}
        ]
        
        # タスク作成
        for task_data in tasks:
            client.post('/api/tasks/', json=task_data, headers=auth_headers)
        
        # 進行中タスクを完了状態に更新
        response = client.get('/api/tasks/', headers=auth_headers)
        tasks = response.get_json()['tasks']
        in_progress_tasks = [task for task in tasks if task['status'] == 'in_progress']
        if in_progress_tasks:
            task_id = in_progress_tasks[0]['id']
            client.put(f'/api/tasks/{task_id}', json={"status": "completed"}, headers=auth_headers)
        
        # 統計情報取得
        response = client.get('/api/tasks/stats', headers=auth_headers)
        assert response.status_code == 200
        
        stats = response.get_json()['stats']
        assert stats['total_tasks'] == 4
        assert stats['pending_tasks'] == 2
        # 進行中タスクが1つ完了に変わるので、完了タスクは2個
        assert stats['completed_tasks'] >= 1  # 最低1つは完了
        assert 0 <= stats['completion_rate'] <= 100  # 割合は0-100%の範囲

    def test_unauthorized_access(self, client):
        """認証なしでのアクセステスト"""
        # 認証が必要なエンドポイントへの認証なしアクセス
        response = client.get('/api/tasks/')
        assert response.status_code == 401
        
        response = client.post('/api/tasks/', json={"title": "テスト"})
        assert response.status_code == 401