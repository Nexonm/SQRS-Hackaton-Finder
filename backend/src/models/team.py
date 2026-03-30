from sqlalchemy import Column, Integer, String, Text

from src.database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    owner_handle = Column(String(64), nullable=False, index=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    required_roles = Column(Text, nullable=True)   # comma-separated roles
    required_skills = Column(Text, nullable=True)  # comma-separated tags
    size_target = Column(Integer, nullable=True)
