from dotenv import load_dotenv
import os
load_dotenv()

class Config:

    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATION = os.getenv('SQLALCHEMY_TRACK_MODIFICATION')
    SECRET_KEY = os.getenv('SECRET_KEY')

class DevelopmentConfig(Config):
    Debug = True

class ProductionConfig(Config):
    Debug = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
        }
