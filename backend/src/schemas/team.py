from pydantic import BaseModel, Field
from typing import Optional

from src.schemas.profile import RoleOut, SkillOut


class TeamCreate(BaseModel):
    owner_handle: str = Field(..., min_length=1, max_length=40)
    title: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=1000)
    size_target: Optional[int] = Field(None, ge=1, le=100)
    required_role_ids: list[int] = Field(default_factory=list, max_length=13)
    required_skill_ids: list[int] = Field(default_factory=list, max_length=20)


class TeamUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=1000)
    size_target: Optional[int] = Field(None, ge=1, le=100)
    required_role_ids: Optional[list[int]] = Field(None, max_length=13)
    required_skill_ids: Optional[list[int]] = Field(None, max_length=20)


class TeamRead(BaseModel):
    id: int
    owner_handle: str
    title: str
    description: Optional[str]
    size_target: Optional[int]
    required_roles: list[RoleOut]
    required_skills: list[SkillOut]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
