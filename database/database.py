from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Boolean,
    ForeignKey, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id            = Column(Integer, primary_key=True, index=True)
    telegram_id   = Column(Integer, unique=True, index=True, nullable=False)
    name          = Column(String, nullable=True)
    registered_at = Column(DateTime, default=datetime.datetime.now)
    active        = Column(Boolean, default=True)
    sex           = Column(String, nullable=True)
    birthday      = Column(DateTime, nullable=True)
    personal_broadcast = Column(Boolean, default=False)

class Broadcast(Base):
    __tablename__ = 'broadcasts'
    id           = Column(Integer, primary_key=True, index=True)
    content_type = Column(String, nullable=True)
    message_text = Column(String, nullable=True)
    file_id      = Column(String, nullable=True)
    sent_at      = Column(DateTime, default=datetime.datetime.now)

class PersonalBroadcast(Base):
    __tablename__ = 'personal_broadcasts'
    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey('users.id'), nullable=False)
    template_id  = Column(Integer, ForeignKey('personal_templates.id'), nullable=False)
    sent_at      = Column(DateTime, default=datetime.datetime.now)

class PersonalTemplate(Base):
    __tablename__ = 'personal_templates'
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, unique=True, nullable=False)
    message_text  = Column(String, nullable=False)
    days_before   = Column(Integer, default=0)

class AdminSchedule(Base):
    __tablename__ = 'admin_schedule'
    id       = Column(Integer, primary_key=True, index=True)
    user_id  = Column(Integer, ForeignKey('users.id'), nullable=False)
    name     = Column(String, nullable=True)
    date     = Column(Date, nullable=False)

class Review(Base):
    __tablename__ = 'reviews'
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey('users.id'), nullable=False)
    name       = Column(String, nullable=True)
    rating     = Column(Integer, nullable=False)
    text       = Column(String, nullable=True)
    photo_file = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

class ActiveSupportChat(Base):
    __tablename__ = "active_support_chats"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    admin_id = Column(Integer)

Base.metadata.create_all(bind=engine)
