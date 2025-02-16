from pydantic import BaseModel, Field
from typing import Annotated, Optional
from uuid import UUID


class AttendanceReq(BaseModel):
    worksite_id: UUID
    employee_id: UUID


class EmployeeCreate(BaseModel):
    first_name: Annotated[str, Field(min_length=3, max_length=64)]
    last_name: Annotated[str, Field(max_length=64)]
    phone: int
    role: Optional[Annotated[str, Field(max_length=36)]] = None
    organization: Optional[Annotated[str, Field(max_length=36)]] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[Annotated[str, Field(min_length=3, max_length=64)]] = None
    last_name: Optional[Annotated[str, Field(max_length=64)]] = None
    phone: Optional[int] = None
    role: Optional[Annotated[str, Field(max_length=36)]] = None
    organization: Optional[Annotated[str, Field(max_length=36)]] = None

class EmployeeRead(EmployeeCreate):
    id: UUID