from typing import Annotated
import uuid

from pydantic import Field
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str


class UserCreate(schemas.BaseUserCreate):
    username: Annotated[str, Field(max_length=24)]


class UserUpdate(schemas.BaseUserUpdate):
    pass
