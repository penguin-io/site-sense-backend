from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class WorksiteCreate(BaseModel):
    name: str
    description: str | None = None
    project_id: UUID


class WorksiteRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_time: datetime
    project_id: UUID


class WorksiteUpdate(BaseModel):
    description: str
