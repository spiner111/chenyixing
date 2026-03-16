from flask import Blueprint, request, jsonify
from app.models.book import Book
from app import db

book_bp = Blueprint('book', __name__)


@book_bp.route('', methods=['GET'])
def get_books():
    """
    获取书籍列表
    支持分页、分类筛选
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category', '')
    
    query = Book.query.filter_by(status=1)
    
    if category:
        query = query.filter_by(category=category)
    
    pagination = query.order_by(Book.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    books = [book.to_dict() for book in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'books': books,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    获取书籍详情
    """
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'code': 404, 'message': '书籍不存在'}), 404
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': book.to_dict()
    })


@book_bp.route('', methods=['POST'])
def create_book():
    """
    发布书籍
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    data = request.get_json()
    
    # 必填字段校验
    required_fields = ['title', 'category', 'condition', 'price', 'delivery_type']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'code': 400, 'message': f'{field}不能为空'}), 400
    
    book = Book(
        title=data['title'].strip(),
        author=data.get('author', '').strip(),
        isbn=data.get('isbn', '').strip(),
        category=data['category'],
        condition=data['condition'],
        price=float(data['price']),
        description=data.get('description', '').strip(),
        stock=data.get('stock', 1),
        delivery_type=data['delivery_type'],
        user_id=int(user_id),
        status=1
    )
    
    # 处理图片
    images = data.get('images', [])
    if images:
        book.set_images(images)
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '发布成功',
        'data': book.to_dict()
    })


@book_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    更新书籍信息
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'code': 404, 'message': '书籍不存在'}), 404
    
    if book.user_id != int(user_id):
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    
    data = request.get_json()
    
    # 更新字段
    if 'title' in data:
        book.title = data['title'].strip()
    if 'author' in data:
        book.author = data['author'].strip()
    if 'isbn' in data:
        book.isbn = data['isbn'].strip()
    if 'category' in data:
        book.category = data['category']
    if 'condition' in data:
        book.condition = data['condition']
    if 'price' in data:
        book.price = float(data['price'])
    if 'description' in data:
        book.description = data['description'].strip()
    if 'stock' in data:
        book.stock = data['stock']
    if 'delivery_type' in data:
        book.delivery_type = data['delivery_type']
    if 'images' in data:
        book.set_images(data['images'])
    if 'status' in data:
        book.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': book.to_dict()
    })


@book_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    删除书籍（软删除，将状态设为0）
    """
    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'code': 404, 'message': '书籍不存在'}), 404
    
    if book.user_id != int(user_id):
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    
    book.status = 0
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@book_bp.route('/search', methods=['GET'])
def search_books():
    """
    搜索书籍
    支持按书名模糊搜索、分类筛选、价格区间、成色筛选
    """
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    condition = request.args.get('condition', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Book.query.filter_by(status=1)
    
    # 书名模糊搜索
    if keyword:
        query = query.filter(Book.title.like(f'%{keyword}%'))
    
    # 分类筛选
    if category:
        query = query.filter_by(category=category)
    
    # 价格区间
    if min_price is not None:
        query = query.filter(Book.price >= min_price)
    if max_price is not None:
        query = query.filter(Book.price <= max_price)
    
    # 成色筛选
    if condition:
        query = query.filter_by(condition=condition)
    
    pagination = query.order_by(Book.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    books = [book.to_dict() for book in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '搜索成功',
        'data': {
            'books': books,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })
