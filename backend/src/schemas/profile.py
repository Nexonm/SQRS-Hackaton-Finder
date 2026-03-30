from pydantic import BaseModel, Field
from typing import Optional


class ProfileCreate(BaseModel):
    handle: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=128)
    bio: Optional[str] = Field(None, max_length=1000)
    skills: Optional[str] = Field(None, max_length=500)
    preferred_roles: Optional[str] = Field(None, max_length=500)
    availability: Optional[str] = Field(None, max_length=32)


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    bio: Optional[str] = Field(None, max_length=1000)
    skills: Optional[str] = Field(None, max_length=500)
    preferred_roles: Optional[str] = Field(None, max_length=500)
    availability: Optional[str] = Field(None, max_length=32)


class ProfileRead(BaseModel):
    id: int
    handle: str
    name: str
    bio: Optional[str]
    skills: Optional[str]
    preferred_roles: Optional[str]
    availability: Optional[str]

    model_config = {"from_attributes": True}
