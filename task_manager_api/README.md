# タスク管理API システム

Flask + SQLiteベースのタスク管理APIシステムです。完全にローカル環境で動作し、外部サービスへの依存はありません。

## 🚀 特徴

- **JWT認証**: セキュアなユーザー認証システム
- **RESTful API**: 標準的なHTTPメソッドとステータスコード
- **SQLite**: 軽量で設定不要のデータベース
- **包括的テスト**: pytest を使った自動テストスイート
- **エラーハンドリング**: 詳細なログ機能とエラー処理
- **バリデーション**: 入力値の検証とサニタイゼーション

## 📊 システム構成

```
task_manager_api/
├── app/
│   ├── models.py          # データベースモデル
│   ├── database.py        # DB設定と初期化
│   ├── config.py          # 環境設定
│   ├── app.py            # メインアプリケーション
│   ├── routers/          # APIルーター
│   │   ├── auth.py       # 認証関連エンドポイント
│   │   ├── tasks.py      # タスク管理エンドポイント
│   │   └── categories.py # カテゴリ管理エンドポイント
│   └── utils/            # ユーティリティ
│       ├── logger.py     # ログ機能
│       ├── validators.py # バリデーション
│       └── decorators.py # デコレータ
├── tests/                # テストスイート
├── logs/                 # ログファイル
└── run.py               # サーバー起動スクリプト
```

## 🛠️ セットアップ

### 1. 仮想環境の作成とアクティベート

```bash
# 仮想環境作成
python3 -m venv task_manager_env

# 仮想環境アクティベート
source task_manager_env/bin/activate  # Linux/Mac
# または
task_manager_env\\Scripts\\activate  # Windows
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. サーバーの起動

```bash
cd task_manager_api
python run.py
```

サーバーは `http://localhost:5001` で起動します。

## 📚 API仕様

### 認証エンドポイント

#### ユーザー登録
- **POST** `/api/auth/register`
- **Body**: `{"username": "string", "email": "string", "password": "string"}`
- **Response**: ユーザー情報とメッセージ

#### ログイン
- **POST** `/api/auth/login`
- **Body**: `{"username": "string", "password": "string"}`
- **Response**: アクセストークン、リフレッシュトークン、ユーザー情報

#### トークン更新
- **POST** `/api/auth/refresh`
- **Headers**: `Authorization: Bearer <refresh_token>`
- **Response**: 新しいアクセストークン

#### ユーザー情報取得
- **GET** `/api/auth/me`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: 現在のユーザー情報

### タスクエンドポイント

#### タスク一覧取得
- **GET** `/api/tasks/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Query Parameters**: `status`, `priority`, `category_id`（オプション）
- **Response**: タスク一覧とカウント

#### タスク作成
- **POST** `/api/tasks/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: 
```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "priority": "low|medium|high|urgent (optional, default: medium)",
  "status": "pending|in_progress|completed|cancelled (optional, default: pending)",
  "category_id": "integer (optional)",
  "due_date": "ISO8601 datetime string (optional)"
}
```

#### タスク詳細取得
- **GET** `/api/tasks/<task_id>`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: タスク詳細情報

#### タスク更新
- **PUT** `/api/tasks/<task_id>`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: 更新したいフィールドのみ（部分更新対応）

#### タスク削除
- **DELETE** `/api/tasks/<task_id>`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: 削除完了メッセージ

#### タスク統計
- **GET** `/api/tasks/stats`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: タスクの統計情報（完了率、ステータス別カウントなど）

### カテゴリエンドポイント

#### カテゴリ一覧取得
- **GET** `/api/categories/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: カテゴリ一覧

#### カテゴリ作成
- **POST** `/api/categories/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: 
```json
{
  "name": "string (required)",
  "color": "#rrggbb hex color (optional, default: #007bff)",
  "description": "string (optional)"
}
```

#### カテゴリ更新
- **PUT** `/api/categories/<category_id>`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: 更新したいフィールドのみ

#### カテゴリ削除
- **DELETE** `/api/categories/<category_id>`
- **Headers**: `Authorization: Bearer <access_token>`
- **Note**: 紐づくタスクが存在する場合は削除不可

#### カテゴリのタスク一覧
- **GET** `/api/categories/<category_id>/tasks`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: 指定カテゴリのタスク一覧

## 🧪 テスト実行

```bash
# 全テスト実行
python -m pytest tests/ -v

# 特定のテストファイルのみ
python -m pytest tests/test_auth.py -v

# カバレッジ付き実行
python -m pytest tests/ --cov=app --cov-report=html
```

## 🔧 動作確認

```bash
# API動作確認スクリプト
python test_api.py
```

## 📝 デフォルトデータ

システム初回起動時に以下のデモデータが作成されます：

- **デモユーザー**: `demo_user` / パスワード: `demo_password`
- **デフォルトカテゴリ**: 仕事、個人、勉強、緊急

## 🔍 ログ

- **アプリケーションログ**: `logs/task_manager.log`
- **エラーログ**: `logs/errors.log`

## ⚙️ 設定

環境変数で設定をカスタマイズできます：

- `FLASK_ENV`: 実行環境（development/testing/production）
- `SECRET_KEY`: Flaskのシークレットキー
- `JWT_SECRET_KEY`: JWT署名用秘密鍵
- `DATABASE_URL`: データベースURL（デフォルト: SQLite）
- `PORT`: サーバーポート（デフォルト: 5000）

## 🚀 本番デプロイ

```bash
# 本番環境での起動
FLASK_ENV=production python run.py

# または Gunicorn を使用
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app.app:create_app('production')"
```

## 🛡️ セキュリティ

- パスワードのハッシュ化（Werkzeug）
- JWT トークンベース認証
- ユーザー認可による データアクセス制限
- 入力値の検証とサニタイゼーション

## 📈 今後の拡張予定

- [ ] WebSocket によるリアルタイム更新
- [ ] ファイルアップロード機能
- [ ] タスクの共有機能
- [ ] 通知システム
- [ ] レポート機能

---

## 🎯 Background Agent での開発について

このプロジェクトはCursor Background Agent機能の実証実験として開発されました。

### 実装された機能
✅ RESTful API設計と実装  
✅ JWT認証システム  
✅ データベース設計（User, Task, Category）  
✅ 包括的テストスイート（29テストケース）  
✅ エラーハンドリングとログ機能  
✅ 入力バリデーション  
✅ API動作確認ツール  

### Background Agent の学習効果
- **継続的開発**: 開発者不在でもシステム構築が進行
- **品質向上**: 自動テスト、ログ機能、エラーハンドリング
- **構造化**: MVCパターンに基づいた整理されたコード構成
- **実用性**: 実際に動作する本格的なAPIシステム