# SQLAlchemy database configuration
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_app(app: Flask):
    """Initialize SQLAlchemy with Flask app"""
    # Configure database
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Production - PostgreSQL
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Development - SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.config['DATABASE']}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
