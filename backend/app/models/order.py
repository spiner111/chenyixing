from app import db
from datetime import datetime


class Order(db.Model):
    """
    订单模型
    存储订单信息
    订单状态: 0-已取消, 1-待付款, 2-待发货, 3-待收货, 4-已完成
    """
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    address = db.relationship('Address', backref='orders')
    
    def get_status_text(self):
        """
        获取状态文本
        """
        status_map = {
            0: '已取消',
            1: '待付款',
            2: '待发货',
            3: '待收货',
            4: '已完成'
        }
        return status_map.get(self.status, '未知状态')
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            'id': self.id,
            'order_no': self.order_no,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else '',
            'book_image': self.book.get_images()[0] if self.book and self.book.get_images() else '',
            'address_id': self.address_id,
            'receiver': self.address.receiver if self.address else '',
            'phone': self.address.phone if self.address else '',
            'address': self.address.address if self.address else '',
            'total_price': self.total_price,
            'status': self.status,
            'status_text': self.get_status_text(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }
