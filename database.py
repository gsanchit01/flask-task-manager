from config import CONFIG
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = CONFIG.SQLALCHEMY_DATABASE_URI
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)