from typing import Annotated, Optional, List
from pydantic import BaseModel, Field, RootModel
from datetime import datetime
from uuid import UUID


class ProjectCreate(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=64)]
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    location: Optional[Annotated[str, Field(max_length=36)]] = None


class ProjectRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    created_time: datetime
    location: str


class ProjectsRead(RootModel):
    root: List[ProjectRead]


class ProjectUpdate(BaseModel):
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    location: Optional[Annotated[str, Field(max_length=36)]] = None
