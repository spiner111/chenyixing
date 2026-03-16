from app import db
from datetime import datetime
import hashlib


class User(db.Model):
    """
    用户模型
    存储用户基本信息
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50), default='')
    avatar = db.Column(db.String(255), default='')
    phone = db.Column(db.String(20), default='')
    email = db.Column(db.String(100), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    books = db.relationship('Book', backref='seller', lazy=True)
    orders = db.relationship('Order', backref='buyer', lazy=True)
    addresses = db.relationship('Address', backref='user', lazy=True)
    
    def set_password(self, password):
        """
        设置密码，使用MD5加密
        """
        self.password = hashlib.md5(password.encode()).hexdigest()
    
    def check_password(self, password):
        """
        验证密码
        """
        return self.password == hashlib.md5(password.encode()).hexdigest()
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'phone': self.phone,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
