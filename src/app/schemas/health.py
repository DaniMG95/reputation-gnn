from pydantic import BaseModel
from enum import Enum

class StatusTypes(str, Enum):
    healthy = "healthy"
    unhealthy = "unhealthy"


class ComponentStatus(BaseModel):
    name: str
    status: StatusTypes


class HealthCheckResponse(BaseModel):
    status: StatusTypes
    components: list[ComponentStatus]

