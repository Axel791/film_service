# models/entity.py
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID


from db.base_class import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
