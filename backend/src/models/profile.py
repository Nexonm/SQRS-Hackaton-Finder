from sqlalchemy import Column, Integer, String, Text

from src.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    handle = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    bio = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)       # comma-separated tags
    preferred_roles = Column(Text, nullable=True)  # comma-separated roles
    availability = Column(String(32), nullable=True)
