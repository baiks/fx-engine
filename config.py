import os
from datetime import timedelta


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or '9f74c1e5b8d24e2b9a1f8b0c5c8e2f1a9d7e6c4b3a2d1f0e4c8b9d7a6e5f4c3b'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fx_engine.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # FX Engine specific settings
    QUOTE_VALIDITY_SECONDS = 60
    SUPPORTED_CURRENCIES = ['USD', 'EUR', 'KES', 'NGN']

    # Spread configuration (in basis points, 1 bp = 0.01%)
    BUY_SPREAD_BPS = 50  # 0.5%
    SELL_SPREAD_BPS = 50  # 0.5%

    # Rate update settings
    EXCHANGE_RATE_API_URL = 'https://api.exchangerate-api.com/v4/latest/'
    RATE_STALENESS_THRESHOLD_HOURS = 24


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # In production, ensure SECRET_KEY and DATABASE_URL are set via environment


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}