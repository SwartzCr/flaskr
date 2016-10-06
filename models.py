from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, DateTime
import datetime
Base = declarative_base()

class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    name = Column(String, ForeignKey('users.name'))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="entries")

class User(Base):
    __tablename__ = 'users'

    name = Column(String, nullable=False, unique=True, primary_key=True)
    password = Column(String,  nullable=False)
    entries = relationship("Entry", back_populates="user")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

