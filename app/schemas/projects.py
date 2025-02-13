from typing import Annotated, Optional, List
from pydantic import BaseModel, Field, RootModel
from datetime import datetime
from uuid import UUID


class ProjectCreate(BaseModel):
    name: Annotated[str, Field(max_length=64)]
    description: Optional[Annotated[str, Field(max_length=512)]] = None


class ProjectRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    created_time: datetime


class ProjectsRead(RootModel):
    root: List[ProjectRead]


class ProjectUpdate(BaseModel):
    description: str
