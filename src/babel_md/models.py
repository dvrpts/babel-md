from enum import Enum

from pydantic import BaseModel


class OutputFormat(str, Enum):
    markdown = "markdown"
    json = "json"


class HealthResponse(BaseModel):
    status: str
    version: str


class ErrorResponse(BaseModel):
    detail: str
