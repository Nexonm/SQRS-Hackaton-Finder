from sqlalchemy import Column, ForeignKey, Integer, String

from src.database import Base


class JoinRequest(Base):
    __tablename__ = "join_requests"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False,
        index=True,
    )
    applicant_handle = Column(
        String(40),
        ForeignKey("profiles.handle", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String(16), nullable=False, default="pending")
    # status values: pending | accepted | rejected
