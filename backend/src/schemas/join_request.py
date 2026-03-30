from pydantic import BaseModel, Field
from typing import Literal


class JoinRequestCreate(BaseModel):
    team_id: int
    applicant_handle: str = Field(..., min_length=1, max_length=64)


class JoinRequestStatusUpdate(BaseModel):
    status: Literal["accepted", "rejected"]


class JoinRequestRead(BaseModel):
    id: int
    team_id: int
    applicant_handle: str
    status: str

    model_config = {"from_attributes": True}
