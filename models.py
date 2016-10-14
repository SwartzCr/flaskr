from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, DateTime, Boolean
import datetime
Base = declarative_base()

class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    name = Column(String, ForeignKey('users.name'))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    tag = Column(String(length=50), ForeignKey('tags.name'), nullable=True)

    user = relationship("User", back_populates="entries")

class User(Base):
    __tablename__ = 'users'

    name = Column(String, nullable=False, unique=True, primary_key=True)
    password = Column(String,  nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    public = Column(Integer, server_default="0", nullable=False)

    entries = relationship("Entry", back_populates="user")
    tags = relationship("Tag", back_populates="user")

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=50), nullable=False)
    username = Column(String, ForeignKey('users.name'), nullable=False)

    user = relationship("User", back_populates="tags")
    entries = relationship("Entry")
