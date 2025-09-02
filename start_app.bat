@echo off
REM Task Manager アプリケーション起動スクリプト (Windows)

echo 🚀 Task Manager アプリケーションを起動しています...

REM 1. バックエンドAPIの起動
echo 📡 バックエンドAPIを起動中...
cd task_manager_api

REM 仮想環境がない場合は作成
if not exist "task_manager_env" (
    echo 🔧 仮想環境を作成中...
    python3 -m venv task_manager_env
)

REM 仮想環境の有効化
call task_manager_env\Scripts\activate.bat

REM 依存関係のインストール/更新
echo 📦 依存関係をインストール中...
pip install -r requirements.txt

REM データベースの初期化（存在しない場合）
if not exist "instance\task_manager.db" (
    echo 🗄️ データベースを初期化中...
    python3 -c "from app.app import create_app; from app.database import db; app = create_app(); app.app_context().push(); db.create_all(); print('データベースを作成しました')"
)

REM バックエンドを背景で起動
echo 🔥 バックエンドAPIを起動中（http://localhost:5001）...
start /B python3 run.py

REM 少し待ってAPIの起動を確認
timeout /t 3 /nobreak >nul

REM 2. フロントエンドの起動
echo 🎨 フロントエンドを起動中...
cd ..\frontend

REM Python HTTPサーバーでフロントエンドを起動
echo 🌐 フロントエンドサーバーを起動中（http://localhost:8080）...
echo 🎉 アプリケーションが起動しました！
echo.
echo 📱 フロントエンド: http://localhost:8080
echo 📡 バックエンドAPI: http://localhost:5001
echo.
echo ブラウザでフロントエンドが自動的に開きます...
echo 終了するには このウィンドウを閉じてください
echo.

REM ブラウザでフロントエンドを開く
start http://localhost:8080

REM フロントエンドサーバーを起動（メインプロセス）
python3 -m http.server 8080