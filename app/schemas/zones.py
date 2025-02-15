from typing import Optional, List, Annotated
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class ZoneCreate(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=64)]
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    feed_uri: Optional[Annotated[str, Field(max_length=512)]] = None
    worksite_id: UUID


class ZoneRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    created_time: datetime
    worksite_id: UUID
    project_id: UUID


class ZonesRead(BaseModel):
    root: List[ZoneRead]


class ZoneUpdate(BaseModel):
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    feed_uri: Optional[Annotated[str, Field(max_length=512)]] = None
