from sqlalchemy import Column, Integer, String, ForeignKey

from src.database import Base


class JoinRequest(Base):
    __tablename__ = "join_requests"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    applicant_handle = Column(String(64), nullable=False)
    status = Column(String(16), nullable=False, default="pending")
    # status values: pending | accepted | rejected
