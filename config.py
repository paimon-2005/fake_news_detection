import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-12345'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fake_news_detector.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Model settings
    MODEL_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'models')
    DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
    
    # Ensure directories exist
    os.makedirs(MODEL_PATH, exist_ok=True)
    os.makedirs(DATA_PATH, exist_ok=True)
