from typing import Annotated, Literal, List, Optional
import uuid

from pydantic import Field, BaseModel
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str
    role: Literal["admin", "padmin", "wadmin"]
    project_ids: List[uuid.UUID]
    worksite_ids: List[uuid.UUID]


class UserCreate(schemas.BaseUserCreate):
    username: Annotated[str, Field(min_length=3, max_length=24)]


class UserUpdate(schemas.BaseUserUpdate):
    pass


class RoleReq(BaseModel):
    user_id: uuid.UUID
    role: Literal["admin", "padmin", "wadmin"]


class AccessReq(BaseModel):
    user_id: uuid.UUID
    resource_ids: List[uuid.UUID]
    resource_type: Literal["project", "worksite", "zone"]
    access: Literal["allow", "deny"]
