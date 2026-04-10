from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from src.database import Base


profile_skills = Table(
    "profile_skills",
    Base.metadata,
    Column(
        "profile_handle",
        String(40),
        ForeignKey("profiles.handle", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
)


class Profile(Base):
    __tablename__ = "profiles"

    handle = Column(String(40), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    contacts = Column(String(300), nullable=True)
    availability = Column(Boolean, nullable=False, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    role = relationship("Role", back_populates="profiles")
    skills = relationship(
        "Skill",
        secondary=profile_skills,
        back_populates="profiles",
    )


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    profiles = relationship(
        "Profile", secondary=profile_skills, back_populates="skills"
    )


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    profiles = relationship("Profile", back_populates="role")
