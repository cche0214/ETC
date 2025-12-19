from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

import uuid

def generate_uuid():
    return str(uuid.uuid4())

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = 'chat_sessions'

    id = Column(String(36), primary_key=True, index=True, default=generate_uuid)
    title = Column(String(200), nullable=False, default="新会话")
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # 定义一对多的关系
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(String(36), primary_key=True, index=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(50), nullable=False) # 'user' 'assistant' 'system' 'tool'
    content = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    session = relationship("ChatSession", back_populates="messages")
