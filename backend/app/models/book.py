from app import db
from datetime import datetime
import json


class Book(db.Model):
    """
    书籍模型
    存储二手书籍信息
    """
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), default='')
    isbn = db.Column(db.String(20), default='')
    category = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, default='')
    stock = db.Column(db.Integer, default=1)
    delivery_type = db.Column(db.String(20), nullable=False)
    images = db.Column(db.Text, default='[]')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    orders = db.relationship('Order', backref='book', lazy=True)
    
    def get_images(self):
        """
        获取图片列表
        """
        try:
            return json.loads(self.images)
        except:
            return []
    
    def set_images(self, images):
        """
        设置图片列表
        """
        self.images = json.dumps(images)
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'category': self.category,
            'condition': self.condition,
            'price': self.price,
            'description': self.description,
            'stock': self.stock,
            'delivery_type': self.delivery_type,
            'images': self.get_images(),
            'user_id': self.user_id,
            'seller': self.seller.nickname if self.seller else '',
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
