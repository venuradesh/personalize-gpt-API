class Config:
    """Base Configuration with default settings"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = ""
    DATABASE_URI = ""

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = ""

class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URI = ""