import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

_pw = quote_plus(os.environ.get('DB_PASSWORD', ''))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'library-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:{_pw}@localhost/library_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FINE_PER_DAY = 5
    LOAN_PERIOD_DAYS = 14
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates')
    STATIC_FOLDER    = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')