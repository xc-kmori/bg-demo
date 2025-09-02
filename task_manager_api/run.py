"""
メインエントリーポイント
開発サーバーの起動
"""
import os
from app.app import create_app

if __name__ == '__main__':
    # 環境設定
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # アプリケーション作成
    app = create_app(config_name)
    
    # 開発サーバー起動
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5001)),
        debug=True if config_name == 'development' else False
    )