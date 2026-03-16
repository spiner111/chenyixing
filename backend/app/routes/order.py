from flask import Blueprint, request, jsonify
from app.models.order import Order
from app.models.book import Book
from app.models.address import Address
from app import db
import random
import string
from datetime import datetime

order_bp = Blueprint('order', __name__)


def generate_order_no():
    """
    生成订单号
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f'CB{timestamp}{random_str}'


@order_bp.route('', methods=['POST'])
def create_order():
    """
    创建订单
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    data = request.get_json()
    book_id = data.get('book_id')
    address_id = data.get('address_id')
    
    if not book_id or not address_id:
        return jsonify({'code': 400, 'message': '书籍ID和地址ID不能为空'}), 400
    
    # 检查书籍
    book = Book.query.get(book_id)
    if not book or book.status != 1:
        return jsonify({'code': 404, 'message': '书籍不存在或已下架'}), 404
    
    if book.stock < 1:
        return jsonify({'code': 400, 'message': '书籍库存不足'}), 400
    
    # 检查地址
    address = Address.query.get(address_id)
    if not address or address.user_id != int(user_id):
        return jsonify({'code': 404, 'message': '地址不存在'}), 404
    
    # 不能购买自己的书
    if book.user_id == int(user_id):
        return jsonify({'code': 400, 'message': '不能购买自己发布的书籍'}), 400
    
    # 创建订单
    order = Order(
        order_no=generate_order_no(),
        user_id=int(user_id),
        book_id=book_id,
        address_id=address_id,
        total_price=book.price,
        status=1
    )
    
    # 减少库存
    book.stock -= 1
    
    db.session.add(order)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '订单创建成功',
        'data': order.to_dict()
    })


@order_bp.route('', methods=['GET'])
def get_orders():
    """
    获取订单列表
    支持按状态筛选
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    status = request.args.get('status', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Order.query.filter_by(user_id=int(user_id))
    
    if status is not None:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    orders = [order.to_dict() for order in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'orders': orders,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    获取订单详情
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.user_id != int(user_id):
        return jsonify({'code': 403, 'message': '无权查看'}), 403
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': order.to_dict()
    })


@order_bp.route('/<int:order_id>/cancel', methods=['PUT'])
def cancel_order(order_id):
    """
    取消订单
    仅待付款状态可取消
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.user_id != int(user_id):
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    
    if order.status != 1:
        return jsonify({'code': 400, 'message': '当前状态不能取消订单'}), 400
    
    # 恢复库存
    book = Book.query.get(order.book_id)
    if book:
        book.stock += 1
    
    order.status = 0
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '订单已取消'
    })


@order_bp.route('/<int:order_id>/pay', methods=['PUT'])
def pay_order(order_id):
    """
    支付订单（模拟）
    待付款 -> 待发货
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.user_id != int(user_id):
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    
    if order.status != 1:
        return jsonify({'code': 400, 'message': '当前状态不能支付'}), 400
    
    order.status = 2
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '支付成功',
        'data': order.to_dict()
    })


@order_bp.route('/<int:order_id>/ship', methods=['PUT'])
def ship_order(order_id):
    """
    发货（模拟）
    待发货 -> 待收货
    """
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.status != 2:
        return jsonify({'code': 400, 'message': '当前状态不能发货'}), 400
    
    order.status = 3
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '发货成功',
        'data': order.to_dict()
    })


@order_bp.route('/<int:order_id>/confirm', methods=['PUT'])
def confirm_order(order_id):
    """
    确认收货
    待收货 -> 已完成
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.user_id != int(user_id):
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    
    if order.status != 3:
        return jsonify({'code': 400, 'message': '当前状态不能确认收货'}), 400
    
    order.status = 4
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '确认收货成功',
        'data': order.to_dict()
    })
