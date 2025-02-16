from typing import Optional, List, Annotated
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class ZoneCreate(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=64)]
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    feed_uri: Optional[Annotated[str, Field(max_length=512)]] = None
    worksite_id: UUID
    activity: Optional[str] = "inactive"
    location: Optional[Annotated[str, Field(max_length=36)]] = None
    lat: Optional[float] = None
    long: Optional[float] = None


class ZoneRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    created_time: datetime
    worksite_id: UUID
    project_id: UUID
    activity: str
    location: Optional[Annotated[str, Field(max_length=36)]] = None
    lat: Optional[float] = None
    long: Optional[float] = None


class ZonesRead(BaseModel):
    root: List[ZoneRead]


class ZoneUpdate(BaseModel):
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    feed_uri: Optional[Annotated[str, Field(max_length=512)]] = None
    activity: Optional[str] = None
    location: Optional[Annotated[str, Field(max_length=36)]] = None
    lat: Optional[float] = None
    long: Optional[float] = None
