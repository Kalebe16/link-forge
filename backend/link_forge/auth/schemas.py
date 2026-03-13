from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# CreateUser
class CreateUserBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class CreateUserInput(CreateUserBody):
    pass


class CreateUserOuput(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime


class CreateUserResp(CreateUserOuput):
    pass


# Login
class LoginBody(BaseModel):
    email: EmailStr
    password: str


class LoginInput(LoginBody):
    pass


class LoginOutput(BaseModel):
    access_token: str
    access_token_expires_at: datetime
    refresh_token: str
    refresh_token_expires_at: datetime


class LoginResp(BaseModel):
    message: str


# Refresh
class RefreshResp(BaseModel):
    message: str


# Me
class MeResp(BaseModel):
    id: int
    email: str
    created_at: datetime


# Logout
class LogoutResp(BaseModel):
    message: str
