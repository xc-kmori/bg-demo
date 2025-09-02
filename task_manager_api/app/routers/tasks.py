"""
タスク管理APIエンドポイント
CRUD操作とタスクステータス管理
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Task, Category
from app.database import db
from app.utils.validators import TaskValidator, ValidationError
from app.utils.decorators import combined_decorator, handle_errors

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """タスク一覧取得"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # クエリパラメータ
        status = request.args.get('status')
        priority = request.args.get('priority')
        category_id = request.args.get('category_id')
        
        # ベースクエリ
        query = Task.query.filter_by(user_id=current_user_id)
        
        # フィルタリング
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)
        if category_id:
            query = query.filter_by(category_id=int(category_id))
            
        tasks = query.order_by(Task.created_at.desc()).all()
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks],
            'total': len(tasks)
        })
        
    except Exception as e:
        return jsonify({'error': f'タスク取得でエラーが発生しました: {str(e)}'}), 500


@tasks_bp.route('/', methods=['POST'])
@jwt_required()
@combined_decorator
def create_task():
    """タスク作成"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # バリデーション実行
    validated_data = TaskValidator.validate_task_data(data)
    title = validated_data['title']
    
    # カテゴリの存在確認
    category_id = data.get('category_id')
    if category_id:
        category = Category.query.filter_by(id=category_id, user_id=current_user_id).first()
        if not category:
            return jsonify({'error': '指定されたカテゴリが見つかりません'}), 404
    
    # 新規タスク作成
    task = Task(
        title=title,
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        status=data.get('status', 'pending'),
        user_id=current_user_id,
        category_id=category_id
    )
    
    # 期限日の設定
    due_date_str = data.get('due_date')
    if due_date_str:
        task.due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'message': 'タスクを作成しました',
        'task': task.to_dict()
    }), 201


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """特定のタスク取得"""
    try:
        current_user_id = int(get_jwt_identity())
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'error': 'タスクが見つかりません'}), 404
            
        return jsonify({'task': task.to_dict()})
        
    except Exception as e:
        return jsonify({'error': f'タスク取得でエラーが発生しました: {str(e)}'}), 500


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """タスク更新"""
    try:
        current_user_id = int(get_jwt_identity())
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'error': 'タスクが見つかりません'}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSONデータが必要です'}), 400
        
        # フィールド更新
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
            # 完了状態の場合、完了日時を設定
            if data['status'] == 'completed':
                task.completed_at = datetime.utcnow()
        if 'priority' in data:
            task.priority = data['priority']
        if 'category_id' in data:
            # カテゴリの存在確認
            if data['category_id']:
                category = Category.query.filter_by(id=data['category_id'], user_id=current_user_id).first()
                if not category:
                    return jsonify({'error': '指定されたカテゴリが見つかりません'}), 404
            task.category_id = data['category_id']
        
        # 期限日の更新
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': '期限日の形式が正しくありません'}), 400
            else:
                task.due_date = None
                
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'タスクを更新しました',
            'task': task.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'タスク更新でエラーが発生しました: {str(e)}'}), 500


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """タスク削除"""
    try:
        current_user_id = int(get_jwt_identity())
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'error': 'タスクが見つかりません'}), 404
            
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'タスクを削除しました'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'タスク削除でエラーが発生しました: {str(e)}'}), 500


@tasks_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """タスク統計情報"""
    try:
        current_user_id = int(get_jwt_identity())
        
        total_tasks = Task.query.filter_by(user_id=current_user_id).count()
        pending_tasks = Task.query.filter_by(user_id=current_user_id, status='pending').count()
        in_progress_tasks = Task.query.filter_by(user_id=current_user_id, status='in_progress').count()
        completed_tasks = Task.query.filter_by(user_id=current_user_id, status='completed').count()
        
        # 優先度別統計
        high_priority = Task.query.filter_by(user_id=current_user_id, priority='high').count()
        urgent_priority = Task.query.filter_by(user_id=current_user_id, priority='urgent').count()
        
        return jsonify({
            'stats': {
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks,
                'in_progress_tasks': in_progress_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0,
                'high_priority_tasks': high_priority,
                'urgent_priority_tasks': urgent_priority
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'統計情報取得でエラーが発生しました: {str(e)}'}), 500