from app import db


class Address(db.Model):
    """
    收货地址模型
    存储用户收货地址信息
    """
    __tablename__ = 'addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    is_default = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'receiver': self.receiver,
            'phone': self.phone,
            'address': self.address,
            'is_default': self.is_default
        }
