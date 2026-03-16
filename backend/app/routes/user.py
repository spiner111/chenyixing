from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db
import re

user_bp = Blueprint('user', __name__)


@user_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    支持校园邮箱(@gzus.edu.cn)或手机号注册
    """
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    nickname = data.get('nickname', '').strip()
    
    # 参数校验
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    
    if len(password) < 6 or len(password) > 20:
        return jsonify({'code': 400, 'message': '密码长度必须在6-20位之间'}), 400
    
    # 验证用户名格式（邮箱或手机号）
    is_email = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', username)
    is_phone = re.match(r'^1[3-9]\d{9}$', username)
    
    if not is_email and not is_phone:
        return jsonify({'code': 400, 'message': '用户名必须是邮箱或手机号'}), 400
    
    # 校园邮箱验证
    if is_email and not username.endswith('@gzus.edu.cn'):
        return jsonify({'code': 400, 'message': '仅支持校园邮箱注册(@gzus.edu.cn)'}), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户已存在'}), 400
    
    # 创建用户
    user = User(
        username=username,
        nickname=nickname if nickname else username.split('@')[0] if '@' in username else username[:3] + '****',
        phone=username if is_phone else '',
        email=username if is_email else ''
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '注册成功',
        'data': {
            'user': user.to_dict(),
            'token': str(user.id)
        }
    })


@user_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    支持邮箱/手机号登录
    """
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
    
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'user': user.to_dict(),
            'token': str(user.id)
        }
    })


@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """
    获取用户信息
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': user.to_dict()
    })


@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """
    更新用户信息
    支持修改昵称和头像
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    if 'nickname' in data:
        user.nickname = data['nickname'].strip()
    if 'avatar' in data:
        user.avatar = data['avatar'].strip()
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': user.to_dict()
    })
