from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
import datetime


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    registered_at = Column(DateTime, default=datetime.datetime.now)
    active = Column(Boolean, default=True)
    sex = Column(String, nullable=True)
    birthday = Column(DateTime, nullable=True)

class Broadcast(Base):
    __tablename__ = 'broadcasts'
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String, nullable=True)
    message_text = Column(String, nullable=True)
    file_id = Column(String, nullable=True)
    sent_at = Column(DateTime, default=datetime.datetime.now)

class PersonalBroadcast(Base):
    __tablename__ = 'personal_broadcasts'
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    sent_at = Column(DateTime, default=datetime.datetime.now)

Base.metadata.create_all(bind=engine)