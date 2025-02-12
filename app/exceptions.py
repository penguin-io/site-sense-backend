from typing import Union, Dict
from enum import Enum
from pydantic import BaseModel


class ErrorModel(BaseModel):
    detai: Union[str, Dict[str, str]]


class ErrorCode(str, Enum):
    PROJECT_NOT_FOUND = "project not found :("
    ADMIN_REQUIRED = "admin access required :("
    PROJECT_NAME_EXISTS = "project with same name already exists :("
