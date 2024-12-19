from pydantic import BaseModel, EmailStr
from schemas import UserSchemaOut


class LoginSchemaIn(BaseModel):
    email: EmailStr
    password: str


class LoginSchemaOut(BaseModel):
    token: str
    user: UserSchemaOut


class ChangePasswordSchemaIn(BaseModel):
    old_password: str
    new_password: str


class ChangePasswordSchemaOut(BaseModel):
    message: str
