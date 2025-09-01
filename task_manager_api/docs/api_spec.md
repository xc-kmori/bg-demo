# API仕様書

## 概要

タスク管理APIは、個人のタスク管理を効率化するためのRESTful APIです。ユーザー認証、タスクのCRUD操作、カテゴリ管理機能を提供します。

## ベースURL

```
http://localhost:5000/api
```

## 認証

JWTトークンベースの認証を使用します。ほとんどのエンドポイントにはアクセストークンが必要です。

### 認証ヘッダー

```
Authorization: Bearer <access_token>
```

## エンドポイント詳細

### 🔐 認証 (`/auth`)

#### ユーザー登録

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "user123",
  "email": "user@example.com",
  "password": "securepassword"
}
```

**レスポンス**:
```json
{
  "message": "ユーザー登録が完了しました",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00.000000",
    "is_active": true
  }
}
```

#### ログイン

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "user123",
  "password": "securepassword"
}
```

**レスポンス**:
```json
{
  "message": "ログインに成功しました",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00.000000",
    "is_active": true
  }
}
```

### 📝 タスク (`/tasks`)

#### タスク一覧取得

```http
GET /api/tasks/?status=pending&priority=high&category_id=1
Authorization: Bearer <token>
```

**クエリパラメータ**:
- `status`: pending, in_progress, completed, cancelled
- `priority`: low, medium, high, urgent  
- `category_id`: カテゴリID

**レスポンス**:
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "重要なタスク",
      "description": "詳細な説明",
      "status": "pending",
      "priority": "high",
      "due_date": "2024-12-31T23:59:59.000000",
      "completed_at": null,
      "created_at": "2024-01-01T00:00:00.000000",
      "updated_at": "2024-01-01T00:00:00.000000",
      "user_id": 1,
      "category_id": 1,
      "category_name": "仕事"
    }
  ],
  "total": 1
}
```

#### タスク作成

```http
POST /api/tasks/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "新しいタスク",
  "description": "タスクの詳細説明",
  "priority": "high",
  "status": "pending",
  "category_id": 1,
  "due_date": "2024-12-31T23:59:59"
}
```

#### タスク統計

```http
GET /api/tasks/stats
Authorization: Bearer <token>
```

**レスポンス**:
```json
{
  "stats": {
    "total_tasks": 10,
    "pending_tasks": 3,
    "in_progress_tasks": 2,
    "completed_tasks": 5,
    "completion_rate": 50.0,
    "high_priority_tasks": 2,
    "urgent_priority_tasks": 1
  }
}
```

### 🏷️ カテゴリ (`/categories`)

#### カテゴリ作成

```http
POST /api/categories/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "新しいカテゴリ",
  "color": "#ff5722",
  "description": "カテゴリの説明"
}
```

**レスポンス**:
```json
{
  "message": "カテゴリを作成しました",
  "category": {
    "id": 1,
    "name": "新しいカテゴリ",
    "color": "#ff5722",
    "description": "カテゴリの説明",
    "user_id": 1,
    "created_at": "2024-01-01T00:00:00.000000",
    "task_count": 0
  }
}
```

#### カテゴリのタスク一覧

```http
GET /api/categories/1/tasks
Authorization: Bearer <token>
```

## ❌ エラーレスポンス

全てのエラーは以下の形式で返されます：

```json
{
  "error": "エラーメッセージ"
}
```

### ステータスコード

- `200`: 成功
- `201`: 作成成功
- `400`: バリデーションエラー
- `401`: 認証エラー
- `404`: リソースが見つからない
- `409`: 競合（重複データなど）
- `422`: 処理不能（JWT関連エラーなど）
- `500`: サーバー内部エラー

## 📊 データモデル

### User（ユーザー）
- `id`: 主キー
- `username`: ユーザー名（ユニーク）
- `email`: メールアドレス（ユニーク）
- `password_hash`: パスワードハッシュ
- `created_at`: 作成日時
- `is_active`: アクティブフラグ

### Task（タスク）
- `id`: 主キー
- `title`: タスクタイトル
- `description`: 詳細説明
- `status`: ステータス
- `priority`: 優先度
- `due_date`: 期限日（オプション）
- `completed_at`: 完了日時（オプション）
- `created_at`: 作成日時
- `updated_at`: 更新日時
- `user_id`: 所有者ID（外部キー）
- `category_id`: カテゴリID（外部キー、オプション）

### Category（カテゴリ）
- `id`: 主キー
- `name`: カテゴリ名
- `color`: HEXカラーコード
- `description`: 説明
- `user_id`: 所有者ID（外部キー）
- `created_at`: 作成日時

## 🔒 セキュリティ考慮事項

1. **パスワード**: Werkzeugを使用してハッシュ化
2. **JWT**: HS256アルゴリズムで署名
3. **認可**: ユーザーは自分のデータのみアクセス可能
4. **バリデーション**: 全入力データの検証
5. **ログ**: セキュリティ関連イベントの記録

## 🚀 使用例

### Python クライアント例

```python
import requests

BASE_URL = "http://localhost:5000/api"

# ユーザー登録
register_data = {
    "username": "myuser",
    "email": "myuser@example.com",
    "password": "mypassword"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)

# ログイン
login_data = {"username": "myuser", "password": "mypassword"}
response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
token = response.json()['access_token']

# タスク作成
headers = {"Authorization": f"Bearer {token}"}
task_data = {
    "title": "重要なタスク",
    "description": "今日中に完了",
    "priority": "high"
}
response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)

# タスク一覧取得
response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
tasks = response.json()['tasks']
```

### cURL例

```bash
# ユーザー登録
curl -X POST http://localhost:5000/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass"}'

# ログイン
curl -X POST http://localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username": "testuser", "password": "testpass"}'

# タスク作成（トークンは上記ログインで取得）
curl -X POST http://localhost:5000/api/tasks/ \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
  -d '{"title": "新しいタスク", "priority": "medium"}'
```