from flask import Flask
from flask_cors import CORS
from .database import init_app as init_database
from .config import config
from .cli import init_db, reset_db

def create_app(config_name=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    config_name = config_name or 'default'
    app.config.from_object(config[config_name])
    
    init_database(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    from .api.routes import auth_bp, product_bp, history_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(history_bp, url_prefix='/api/history')
    
    app.cli.add_command(init_db)
    app.cli.add_command(reset_db)
    
    return app