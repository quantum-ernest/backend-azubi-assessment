from datetime import datetime

from pydantic import BaseModel, EmailStr

from schemas import RoleSchemaOut


class UserSchemaIn(BaseModel):
    email: EmailStr
    name: str
    password: str
    confirm_password: str


class UserSchemaOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    created_at: datetime
    role_rel: RoleSchemaOut
