from pydantic import BaseModel, Field
from typing import Optional


class TeamCreate(BaseModel):
    owner_handle: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=1000)
    required_roles: Optional[str] = Field(None, max_length=500)
    required_skills: Optional[str] = Field(None, max_length=500)
    size_target: Optional[int] = Field(None, ge=1, le=100)


class TeamUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=1000)
    required_roles: Optional[str] = Field(None, max_length=500)
    required_skills: Optional[str] = Field(None, max_length=500)
    size_target: Optional[int] = Field(None, ge=1, le=100)


class TeamRead(BaseModel):
    id: int
    owner_handle: str
    title: str
    description: Optional[str]
    required_roles: Optional[str]
    required_skills: Optional[str]
    size_target: Optional[int]

    model_config = {"from_attributes": True}
