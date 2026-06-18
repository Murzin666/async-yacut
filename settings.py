import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', default='1234test4321')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        default='sqlite:///yacut.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DISK_TOKEN = os.getenv('DISK_TOKEN', default='')
    MAX_CUSTOM_ID_LENGTH = 16
    WTF_CSRF_ENABLED = False
    YANDEX_DISK_BASE_PATH = 'YaCut'