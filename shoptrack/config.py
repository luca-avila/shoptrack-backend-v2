import os
from datetime import timedelta

class Config:
    """Base config class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///shoptrack.db')

    PERMANENT_SESSION_LIFETIME = timedelta(days=30)

    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

class DevelopmentConfig(Config):
    """Development config class"""
    DEBUG = True
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///shoptrack.db')

class ProductionConfig(Config):
    """Production config class"""
    DEBUG = False

class TestingConfig(Config):
    """Testing config class"""
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}