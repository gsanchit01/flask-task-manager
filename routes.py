import hashlib
from database import Session
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import Users, Tasks
from logger import logger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import cast
from datetime import datetime

app_routes = Blueprint('app_routes', __name__)



@app_routes.route('/register', methods=['POST'])
def register():
    logger.info('Register endpoint called')
    session = Session()
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not (username and email and password):
        logger.error('Registration failed: Missing fields')
        return jsonify({"message": "All fields (username, email, password) are required"}), 400
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    new_user = Users(username=username, email=email, password=hashed_password)
    session.add(new_user)
    session.commit()
    logger.info('New user registered')
    return jsonify({"message": "User created successfully"}), 201



@app_routes.route('/login', methods=['POST'])
def login():
    logger.info('Login endpoint called')
    session = Session()
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = session.query(Users).filter_by(username=username).first()
    if user and user.password == hashlib.sha256(password.encode()).hexdigest():
        access_token = create_access_token(identity=user.id)
        logger.info('User logged in')
        return jsonify({
            "access_token": access_token,
            "email": user.email,
            "username": user.username
        }), 200
    else:
        logger.error('Login failed: Invalid username or password')
        return jsonify({"message": "Invalid username or password"}), 401



@app_routes.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    logger.info('Get users endpoint called')
    current_user_id = get_jwt_identity()
    session = Session()
    
    users = session.query(Users).all()
    
    user_list = []
    for user in users:
        if user.id != current_user_id:
            user_list.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
            })
    logger.info('Users retrieved')
    return jsonify(user_list), 200



@app_routes.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    logger.info('Get tasks endpoint called')
    current_user_id = get_jwt_identity()
    logger.info(f'Current user ID: {current_user_id}')
    session = Session()
    
    tasks = session.query(Tasks).filter(
    (Tasks.user_id == current_user_id) |
    (cast(Tasks.add_users, JSONB).contains([str(current_user_id)]))
    ).all()
    task_list = []
    for task in tasks:
        task_list.append({
            "id": task.id,
            "task": task.task,
            "created_at": task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": task.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            "is_completed": task.is_completed,
            "add_users": task.add_users,
        })
    logger.info('Tasks retrieved')
    return jsonify({"tasks": task_list}), 200



@app_routes.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    logger.info('Create task endpoint called')
    current_user_id = get_jwt_identity()
    session = Session()
    data = request.json
    task = data.get('task')
    add_users = data.get('add_users', [])
    new_task = Tasks(task=task, user_id=current_user_id, add_users=add_users)
    session.add(new_task)
    session.commit()
    logger.info('New task created')
    return jsonify({"message": "Task created successfully"}), 201



@app_routes.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def edit_task(task_id):
    logger.info('Edit task endpoint called')
    current_user_id = get_jwt_identity()
    session = Session()
    task = session.query(Tasks).filter_by(id=task_id)
    task = task.filter(
    (Tasks.user_id == current_user_id) |
    (cast(Tasks.add_users, JSONB).contains([str(current_user_id)]))
    ).first()
    if not task:
        logger.error('Task not found')
        return jsonify({"message": "Task not found"}), 404
    data = request.json
    task.task = data.get('task', task.task)
    task.add_users = data.get('add_users', task.add_users)
    task.updated_at = datetime.utcnow()
    session.commit()
    logger.info('Task updated successfully')
    return jsonify({"message": "Task updated successfully"}), 200



@app_routes.route('/tasks/<int:task_id>', methods=['PATCH'])
@jwt_required()
def mark_completed(task_id):
    logger.info('Mark task completed endpoint called')
    current_user_id = get_jwt_identity()
    session = Session()
    task = session.query(Tasks).filter_by(id=task_id)
    task = task.filter(
    (Tasks.user_id == current_user_id) |
    (cast(Tasks.add_users, JSONB).contains([str(current_user_id)]))
    ).first()
    if not task:
        logger.error('Task not found')
        return jsonify({"message": "Task not found"}), 404
    if task.is_completed:
        task.is_completed = False
        task.updated_at = datetime.utcnow()
        data = {"message": "Task marked as not completed"}
    else:
        task.is_completed = True
        task.updated_at = datetime.utcnow()
        data = {"message": "Task marked as completed"}
    session.commit()
    logger.info('Task status updated')
    return jsonify(data), 200



@app_routes.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    logger.info('Delete task endpoint called')
    current_user_id = get_jwt_identity()
    session = Session()
    task = session.query(Tasks).filter_by(id=task_id).first()
    if not task:
        logger.error('Task not found')
        return jsonify({"message": "Task not found"}), 404
    if task.user_id != current_user_id:
        logger.error('User does not have permission to delete this task')
        return jsonify({"message": "You do not have permission to delete this task"}), 403
    session.delete(task)
    session.commit()
    logger.info('Task deleted successfully')
    return jsonify({"message": "Task deleted successfully"}), 200
