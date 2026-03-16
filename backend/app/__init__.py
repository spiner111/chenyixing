from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()


def create_app():
    """
    创建Flask应用实例
    """
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = 'campus-book-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'campus_book.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    from app.routes.user import user_bp
    from app.routes.book import book_bp
    from app.routes.order import order_bp
    from app.routes.address import address_bp
    
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(book_bp, url_prefix='/api/books')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(address_bp, url_prefix='/api/addresses')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
