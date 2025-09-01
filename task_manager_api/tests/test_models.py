"""
モデル機能のテスト
データベースモデルの動作テスト
"""
import pytest
from datetime import datetime
from app.models import User, Task, Category
from app.database import db


class TestUserModel:
    """Userモデルのテスト"""

    def test_user_creation(self, app):
        """ユーザー作成テスト"""
        with app.app_context():
            user = User(username='test_model_user', email='model@test.com')
            user.set_password('test_password')
            
            assert user.username == 'test_model_user'
            assert user.email == 'model@test.com'
            assert user.password_hash != 'test_password'  # ハッシュ化されている
            assert user.check_password('test_password') == True
            assert user.check_password('wrong_password') == False

    def test_user_to_dict(self, app):
        """ユーザー辞書変換テスト"""
        with app.app_context():
            user = User(username='dict_test_user', email='dict@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            assert 'id' in user_dict
            assert user_dict['username'] == 'dict_test_user'
            assert user_dict['email'] == 'dict@test.com'
            assert 'password_hash' not in user_dict  # パスワードハッシュは除外
            assert user_dict['is_active'] == True


class TestTaskModel:
    """Taskモデルのテスト"""

    def test_task_creation(self, app):
        """タスク作成テスト"""
        with app.app_context():
            user = User(username='task_test_user', email='task@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            task = Task(
                title='テストタスク',
                description='テスト説明',
                priority='high',
                user_id=user.id
            )
            db.session.add(task)
            db.session.commit()
            
            assert task.title == 'テストタスク'
            assert task.status == 'pending'  # デフォルト値
            assert task.priority == 'high'
            assert task.user_id == user.id

    def test_task_mark_completed(self, app):
        """タスク完了マーク機能のテスト"""
        with app.app_context():
            user = User(username='complete_test_user', email='complete@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            task = Task(title='完了予定タスク', user_id=user.id)
            db.session.add(task)
            db.session.commit()
            
            # 完了前の確認
            assert task.status != 'completed'
            assert task.completed_at is None
            
            # 完了マーク
            task.mark_completed()
            
            # 完了後の確認
            assert task.status == 'completed'
            assert task.completed_at is not None
            assert isinstance(task.completed_at, datetime)


class TestCategoryModel:
    """Categoryモデルのテスト"""

    def test_category_creation(self, app):
        """カテゴリ作成テスト"""
        with app.app_context():
            user = User(username='cat_test_user', email='cat@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            category = Category(
                name='テストカテゴリ',
                color='#ff0000',
                description='テスト用カテゴリ',
                user_id=user.id
            )
            db.session.add(category)
            db.session.commit()
            
            assert category.name == 'テストカテゴリ'
            assert category.color == '#ff0000'
            assert category.user_id == user.id

    def test_category_to_dict_with_task_count(self, app):
        """カテゴリ辞書変換（タスク数含む）のテスト"""
        with app.app_context():
            user = User(username='count_test_user', email='count@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            category = Category(name='カウントテストカテゴリ', user_id=user.id)
            db.session.add(category)
            db.session.commit()
            
            # タスクを2つ作成
            task1 = Task(title='タスク1', user_id=user.id, category_id=category.id)
            task2 = Task(title='タスク2', user_id=user.id, category_id=category.id)
            db.session.add_all([task1, task2])
            db.session.commit()
            
            category_dict = category.to_dict()
            assert category_dict['name'] == 'カウントテストカテゴリ'
            assert category_dict['task_count'] == 2