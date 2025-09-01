"""
カテゴリ管理APIエンドポイント
カテゴリのCRUD操作
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Category, Task
from app.database import db

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/', methods=['GET'])
@jwt_required()
def get_categories():
    """カテゴリ一覧取得"""
    try:
        current_user_id = get_jwt_identity()
        categories = Category.query.filter_by(user_id=current_user_id).order_by(Category.name).all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        })
        
    except Exception as e:
        return jsonify({'error': f'カテゴリ取得でエラーが発生しました: {str(e)}'}), 500


@categories_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    """カテゴリ作成"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSONデータが必要です'}), 400
            
        name = data.get('name')
        if not name:
            return jsonify({'error': 'カテゴリ名は必須項目です'}), 400
            
        # 同名カテゴリの存在チェック
        existing_category = Category.query.filter_by(name=name, user_id=current_user_id).first()
        if existing_category:
            return jsonify({'error': 'このカテゴリ名は既に存在します'}), 409
            
        # 新規カテゴリ作成
        category = Category(
            name=name,
            color=data.get('color', '#007bff'),
            description=data.get('description', ''),
            user_id=current_user_id
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'カテゴリを作成しました',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'カテゴリ作成でエラーが発生しました: {str(e)}'}), 500


@categories_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """カテゴリ更新"""
    try:
        current_user_id = get_jwt_identity()
        category = Category.query.filter_by(id=category_id, user_id=current_user_id).first()
        
        if not category:
            return jsonify({'error': 'カテゴリが見つかりません'}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSONデータが必要です'}), 400
        
        # フィールド更新
        if 'name' in data:
            # 同名カテゴリチェック（自分以外）
            existing = Category.query.filter_by(name=data['name'], user_id=current_user_id).first()
            if existing and existing.id != category_id:
                return jsonify({'error': 'このカテゴリ名は既に存在します'}), 409
            category.name = data['name']
            
        if 'color' in data:
            category.color = data['color']
        if 'description' in data:
            category.description = data['description']
            
        db.session.commit()
        
        return jsonify({
            'message': 'カテゴリを更新しました',
            'category': category.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'カテゴリ更新でエラーが発生しました: {str(e)}'}), 500


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """カテゴリ削除"""
    try:
        current_user_id = get_jwt_identity()
        category = Category.query.filter_by(id=category_id, user_id=current_user_id).first()
        
        if not category:
            return jsonify({'error': 'カテゴリが見つかりません'}), 404
            
        # カテゴリに紐づいているタスクがあるかチェック
        task_count = Task.query.filter_by(category_id=category_id).count()
        if task_count > 0:
            return jsonify({'error': f'このカテゴリには {task_count} 個のタスクが存在するため削除できません'}), 409
            
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': 'カテゴリを削除しました'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'カテゴリ削除でエラーが発生しました: {str(e)}'}), 500


@categories_bp.route('/<int:category_id>/tasks', methods=['GET'])
@jwt_required()
def get_category_tasks(category_id):
    """特定カテゴリのタスク一覧"""
    try:
        current_user_id = get_jwt_identity()
        
        # カテゴリの存在確認
        category = Category.query.filter_by(id=category_id, user_id=current_user_id).first()
        if not category:
            return jsonify({'error': 'カテゴリが見つかりません'}), 404
        
        tasks = Task.query.filter_by(category_id=category_id, user_id=current_user_id).order_by(Task.created_at.desc()).all()
        
        return jsonify({
            'category': category.to_dict(),
            'tasks': [task.to_dict() for task in tasks]
        })
        
    except Exception as e:
        return jsonify({'error': f'カテゴリタスク取得でエラーが発生しました: {str(e)}'}), 500