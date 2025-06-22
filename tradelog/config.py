import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = os.environ.get('SERVER_NAME', 'tradelog.onrender.com')
    CLIENT_ID = os.environ.get('CLIENT_ID', 'fallback-secret')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET', 'fallback-secret')


