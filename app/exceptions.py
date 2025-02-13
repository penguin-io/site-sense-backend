from typing import Union, Dict
from enum import Enum
from pydantic import BaseModel


class InvalidProjectError(Exception):
    pass


class InvalidWorksiteError(Exception):
    pass


class ErrorModel(BaseModel):
    detail: Union[str, Dict[str, str]]


class ErrorCode(str, Enum):
    ADMIN_REQUIRED = "admin access required :("
    PROJECT_NOT_FOUND = "project not found :("
    PROJECT_NAME_EXISTS = "project with same name already exists :("
    WORKSITE_NOT_FOUND = "worksite not found :("
    WORKSITE_NAME_EXISTS = "worksite with same name already exists :("
    ZONE_NOT_FOUND = "zone not found :("
    ZONE_NAME_EXISTS = "zone with same name already exists :("
