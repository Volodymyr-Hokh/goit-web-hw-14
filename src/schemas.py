from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class ContactRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=20)
    last_name: str = Field(max_length=20)
    email: Optional[EmailStr]
    phone_number: Optional[str] = Field(pattern=r"^\+?[1-9][\d]{11}$")
    birthday: Optional[date]


class ContactResponse(ContactRequest):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: str
    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class EmailModel(BaseModel):
    email: EmailStr


class RequestEmail(BaseModel):
    email: EmailStr


class UpdatePassword(BaseModel):
    old_password: str = Field(min_length=6, max_length=10)
    new_password: str = Field(min_length=6, max_length=10)
