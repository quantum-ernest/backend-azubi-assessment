from datetime import datetime

from pydantic import BaseModel


class RoleSchemaOut(BaseModel):
    id: int
    name: str
    created_at: datetime
