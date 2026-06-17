import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///yacut.db')
    DISK_TOKEN = os.getenv('DISK_TOKEN')
    MAX_CUSTOM_ID_LENGTH = 16