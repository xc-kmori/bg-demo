#!/bin/bash

# Task Manager アプリケーション起動スクリプト

echo "🚀 Task Manager アプリケーションを起動しています..."

# 1. バックエンドAPIの起動
echo "📡 バックエンドAPIを起動中..."
cd task_manager_api

# 仮想環境がない場合は作成
if [ ! -d "task_manager_env" ]; then
    echo "🔧 仮想環境を作成中..."
    python -m venv task_manager_env
fi

# 仮想環境の有効化
source task_manager_env/bin/activate

# 依存関係のインストール/更新
echo "📦 依存関係をインストール中..."
pip install -r requirements.txt

# データベースの初期化（存在しない場合）
if [ ! -f "instance/task_manager.db" ]; then
    echo "🗄️ データベースを初期化中..."
    python -c "
from app.app import create_app
from app.database import db

app = create_app()
with app.app_context():
    db.create_all()
    print('データベースを作成しました')
"
fi

# バックエンドを背景で起動
echo "🔥 バックエンドAPIを起動中（http://localhost:5000）..."
python run.py &
BACKEND_PID=$!

# 少し待ってAPIの起動を確認
sleep 3

# ヘルスチェック
echo "🔍 APIヘルスチェック中..."
if curl -s http://localhost:5000/health > /dev/null; then
    echo "✅ バックエンドAPIが正常に起動しました"
else
    echo "❌ バックエンドAPIの起動に失敗しました"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 2. フロントエンドの起動
echo "🎨 フロントエンドを起動中..."
cd ../frontend

# Python HTTPサーバーでフロントエンドを起動
echo "🌐 フロントエンドサーバーを起動中（http://localhost:8080）..."
python -m http.server 8080 &
FRONTEND_PID=$!

echo ""
echo "🎉 アプリケーションが起動しました！"
echo ""
echo "📱 フロントエンド: http://localhost:8080"
echo "📡 バックエンドAPI: http://localhost:5000"
echo "📚 API仕様書: http://localhost:5000/health"
echo ""
echo "終了するには Ctrl+C を押してください"
echo ""

# 終了シグナルをキャッチして両方のプロセスを終了
trap 'echo ""; echo "🛑 アプリケーションを終了中..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

# フロントエンドのプロセスを待機
wait $FRONTEND_PID