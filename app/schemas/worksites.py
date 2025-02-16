from typing import List, Annotated, Optional
from pydantic import BaseModel, RootModel, Field
from datetime import datetime
from uuid import UUID


class WorksiteCreate(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=64)]
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    project_id: UUID
    lat: Optional[float] = None
    long: Optional[float] = None
    status: Optional[bool] = False


class WorksiteRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    created_time: datetime
    project_id: UUID
    lat: Optional[float] = None
    long: Optional[float] = None
    status: Optional[bool] = False


class WorksiteUpdate(BaseModel):
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    lat: Optional[float] = None
    long: Optional[float] = None
    status: Optional[bool] = False


class WorksitesRead(RootModel):
    root: List[WorksiteRead]
