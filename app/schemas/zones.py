from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class ZoneCreate(BaseModel):
    name: str
    description: str | None = None
    feed_uri: str
    worksite_id: int


class ZoneRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_time: datetime
    worksite_id: int
    project_id: UUID


class ZoneUpdate(BaseModel):
    description: Optional[str] = None
    feed_uri: Optional[str] = None
