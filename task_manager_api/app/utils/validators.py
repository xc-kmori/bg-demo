"""
入力値バリデーション機能
APIエンドポイントの入力値検証
"""
import re
from datetime import datetime
from typing import Dict, Any, List, Optional


class ValidationError(Exception):
    """バリデーションエラー"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)


class TaskValidator:
    """タスク関連のバリデーション"""
    
    VALID_STATUSES = {'pending', 'in_progress', 'completed', 'cancelled'}
    VALID_PRIORITIES = {'low', 'medium', 'high', 'urgent'}
    
    @staticmethod
    def validate_task_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """タスクデータのバリデーション"""
        errors = []
        
        # タイトル検証
        if not data.get('title') or not data['title'].strip():
            errors.append('タスクタイトルは必須項目です')
        elif len(data['title']) > 200:
            errors.append('タスクタイトルは200文字以内で入力してください')
        
        # ステータス検証
        status = data.get('status')
        if status and status not in TaskValidator.VALID_STATUSES:
            errors.append(f'ステータスは {", ".join(TaskValidator.VALID_STATUSES)} のいずれかである必要があります')
        
        # 優先度検証
        priority = data.get('priority')
        if priority and priority not in TaskValidator.VALID_PRIORITIES:
            errors.append(f'優先度は {", ".join(TaskValidator.VALID_PRIORITIES)} のいずれかである必要があります')
        
        # 説明文の長さチェック
        description = data.get('description', '')
        if len(description) > 1000:
            errors.append('タスクの説明は1000文字以内で入力してください')
        
        # 期限日検証（YYYY-MM-DD 形式）
        due_date = data.get('due_date')
        if due_date:
            try:
                parsed_date = datetime.strptime(due_date, '%Y-%m-%d') if len(due_date) == 10 else datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                # 過去日チェック: 日単位のため時分は考慮しない
                if parsed_date.date() < datetime.now().date():
                    errors.append('期限日は本日以降の日付を設定してください')
            except ValueError:
                errors.append('期限日の形式が正しくありません（YYYY-MM-DD）')
        
        if errors:
            raise ValidationError('; '.join(errors))
        
        return data


class UserValidator:
    """ユーザー関連のバリデーション"""
    
    @staticmethod
    def validate_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
        """ユーザー登録データのバリデーション"""
        errors = []
        
        # ユーザー名検証
        username = data.get('username', '').strip()
        if not username:
            errors.append('ユーザー名は必須項目です')
        elif len(username) < 3:
            errors.append('ユーザー名は3文字以上である必要があります')
        elif len(username) > 50:
            errors.append('ユーザー名は50文字以内である必要があります')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('ユーザー名は英数字とアンダースコアのみ使用できます')
        
        # メールアドレス検証
        email = data.get('email', '').strip()
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email:
            errors.append('メールアドレスは必須項目です')
        elif not re.match(email_regex, email):
            errors.append('有効なメールアドレスを入力してください')
        elif len(email) > 120:
            errors.append('メールアドレスは120文字以内である必要があります')
        
        # パスワード検証
        password = data.get('password', '')
        if not password:
            errors.append('パスワードは必須項目です')
        elif len(password) < 8:
            errors.append('パスワードは8文字以上である必要があります')
        elif len(password) > 128:
            errors.append('パスワードは128文字以内である必要があります')
        
        if errors:
            raise ValidationError('; '.join(errors))
        
        # 正規化されたデータを返す
        return {
            'username': username,
            'email': email.lower(),
            'password': password
        }


class CategoryValidator:
    """カテゴリ関連のバリデーション"""
    
    @staticmethod
    def validate_category_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """カテゴリデータのバリデーション"""
        errors = []
        
        # カテゴリ名検証
        name = data.get('name', '').strip()
        if not name:
            errors.append('カテゴリ名は必須項目です')
        elif len(name) > 50:
            errors.append('カテゴリ名は50文字以内である必要があります')
        
        # 色コード検証
        color = data.get('color', '#007bff')
        color_regex = r'^#[0-9a-fA-F]{6}$'
        if not re.match(color_regex, color):
            errors.append('色は#rrggbb形式のHEXカラーコードで入力してください')
        
        # 説明文の長さチェック
        description = data.get('description', '')
        if len(description) > 500:
            errors.append('カテゴリの説明は500文字以内で入力してください')
        
        if errors:
            raise ValidationError('; '.join(errors))
        
        return {
            'name': name,
            'color': color,
            'description': description
        }