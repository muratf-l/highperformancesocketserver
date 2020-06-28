from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime

from AppStartup import Base


class User(Base):
    __tablename__ = 'ZUsers'

    UserId = Column(Integer, primary_key=True)
    UserToken = Column(String)
    PlatformId = Column(String, nullable=True)
    NameFirst = Column(String)
    NameLast = Column(String, nullable=True)
    Email = Column(String, nullable=True)
    ProfileImageUrl = Column(String, nullable=True)
    Locale = Column(String, nullable=True)
    Password = Column(String, nullable=True)
    RegisterStatus = Column(Integer)
    OnlineStatus = Column(Integer)
    RegisterMethod = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
