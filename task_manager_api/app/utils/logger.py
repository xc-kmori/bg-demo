"""
ロギング設定
アプリケーション全体のログ管理
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


class TaskManagerLogger:
    """タスク管理API用のロガー"""
    
    def __init__(self, name='task_manager', log_level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # ログフォーマット
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # ファイルハンドラー（ログディレクトリ作成）
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / 'task_manager.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # エラーログ用ハンドラー
        error_handler = logging.FileHandler(log_dir / 'errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # ハンドラー追加（重複チェック）
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
            self.logger.addHandler(error_handler)
    
    def info(self, message):
        """情報ログ"""
        self.logger.info(message)
    
    def warning(self, message):
        """警告ログ"""
        self.logger.warning(message)
    
    def error(self, message):
        """エラーログ"""
        self.logger.error(message)
    
    def debug(self, message):
        """デバッグログ"""
        self.logger.debug(message)
    
    def log_api_request(self, endpoint, method, user_id=None):
        """API リクエストのログ"""
        user_info = f" (User: {user_id})" if user_id else ""
        self.info(f"API Request: {method} {endpoint}{user_info}")
    
    def log_api_error(self, endpoint, error_msg, user_id=None):
        """API エラーのログ"""
        user_info = f" (User: {user_id})" if user_id else ""
        self.error(f"API Error: {endpoint}{user_info} - {error_msg}")


# シングルトンインスタンス
logger = TaskManagerLogger()