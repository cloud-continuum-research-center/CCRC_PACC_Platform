from flask import Flask
from flask_cors import CORS
from config import Config
from .extensions import db
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate  # Import Migrate
import logging
import os
from logging.handlers import RotatingFileHandler
from .utils import fetch_and_store_node_data



def create_app():
    
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['DEBUG'] = True
    app.config['JWT_SECRET_KEY'] = '123456'  # Change this!
    jwt = JWTManager(app)
    
    db.init_app(app)
    CORS(app)
    
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('Application startup')
    
    migrate = Migrate(app, db)  # Initialize Migrate here
    
    with app.app_context():
        from .models import User
        db.create_all()
        fetch_and_store_node_data()

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app