from datetime import datetime

from pydantic import BaseModel, EmailStr, HttpUrl


class User(BaseModel):
    id: int | None = None
    email: EmailStr
    password_hash: str
    created_at: datetime


class Link(BaseModel):
    id: int | None = None
    user_id: int
    url: HttpUrl
    created_at: datetime | None = None
    updated_at: datetime | None = None
