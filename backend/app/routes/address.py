from flask import Blueprint, request, jsonify
from app.models.address import Address
from app import db

address_bp = Blueprint('address', __name__)


@address_bp.route('', methods=['GET'])
def get_addresses():
    """
    获取用户地址列表
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    addresses = Address.query.filter_by(user_id=int(user_id)).all()
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [addr.to_dict() for addr in addresses]
    })


@address_bp.route('', methods=['POST'])
def create_address():
    """
    新增收货地址
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    data = request.get_json()
    
    # 必填字段校验
    required_fields = ['receiver', 'phone', 'address']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'code': 400, 'message': f'{field}不能为空'}), 400
    
    # 如果是第一个地址，设为默认
    is_default = data.get('is_default', 0)
    existing_count = Address.query.filter_by(user_id=int(user_id)).count()
    if existing_count == 0:
        is_default = 1
    
    # 如果设为默认，取消其他默认地址
    if is_default:
        Address.query.filter_by(user_id=int(user_id), is_default=1).update({'is_default': 0})
    
    address = Address(
        user_id=int(user_id),
        receiver=data['receiver'].strip(),
        phone=data['phone'].strip(),
        address=data['address'].strip(),
        is_default=is_default
    )
    
    db.session.add(address)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '添加成功',
        'data': address.to_dict()
    })


@address_bp.route('/<int:address_id>', methods=['PUT'])
def update_address(address_id):
    """
    更新收货地址
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    address = Address.query.get(address_id)
    if not address:
        return jsonify({'code': 404, 'message': '地址不存在'}), 404
    
    if address.user_id != int(user_id):
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    
    data = request.get_json()
    
    if 'receiver' in data:
        address.receiver = data['receiver'].strip()
    if 'phone' in data:
        address.phone = data['phone'].strip()
    if 'address' in data:
        address.address = data['address'].strip()
    if 'is_default' in data:
        # 如果设为默认，取消其他默认地址
        if data['is_default']:
            Address.query.filter_by(user_id=int(user_id), is_default=1).update({'is_default': 0})
        address.is_default = data['is_default']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': address.to_dict()
    })


@address_bp.route('/<int:address_id>', methods=['DELETE'])
def delete_address(address_id):
    """
    删除收货地址
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    address = Address.query.get(address_id)
    if not address:
        return jsonify({'code': 404, 'message': '地址不存在'}), 404
    
    if address.user_id != int(user_id):
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    
    db.session.delete(address)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@address_bp.route('/<int:address_id>/default', methods=['PUT'])
def set_default_address(address_id):
    """
    设置默认地址
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    address = Address.query.get(address_id)
    if not address:
        return jsonify({'code': 404, 'message': '地址不存在'}), 404
    
    if address.user_id != int(user_id):
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    
    # 取消其他默认地址
    Address.query.filter_by(user_id=int(user_id), is_default=1).update({'is_default': 0})
    
    address.is_default = 1
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '设置成功',
        'data': address.to_dict()
    })
