from pydantic import BaseModel, Field
from typing import Optional


class ProfileCreate(BaseModel):
    handle: str = Field(..., pattern=r"^[a-z0-9_-]{3,40}$")
    name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    contacts: Optional[str] = Field(None, max_length=300)
    availability: bool = True
    role_id: int
    skill_ids: list[int] = Field(default_factory=list, max_length=20)


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    contacts: Optional[str] = Field(None, max_length=300)
    availability: Optional[bool] = None
    role_id: Optional[int] = None
    skill_ids: Optional[list[int]] = Field(None, max_length=20)


class SkillOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class RoleOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ProfileRead(BaseModel):
    handle: str
    name: str
    bio: Optional[str]
    contacts: Optional[str]
    availability: bool
    role: RoleOut
    skills: list[SkillOut]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
