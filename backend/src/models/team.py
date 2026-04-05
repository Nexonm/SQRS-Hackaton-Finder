from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from src.database import Base


team_skills = Table(
    "team_skills",
    Base.metadata,
    Column(
        "team_id",
        Integer,
        ForeignKey("teams.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
)

team_roles = Table(
    "team_roles",
    Base.metadata,
    Column(
        "team_id",
        Integer,
        ForeignKey("teams.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_handle = Column(
        String(40),
        ForeignKey("profiles.handle", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    size_target = Column(Integer, nullable=True)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    required_skills = relationship(
        "Skill", secondary=team_skills, backref="teams"
    )
    required_roles = relationship(
        "Role", secondary=team_roles, backref="teams"
    )
