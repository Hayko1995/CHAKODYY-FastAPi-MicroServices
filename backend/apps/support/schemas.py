import datetime
from enum import Enum
from typing import Optional
import pydantic


class UserBase(pydantic.BaseModel):
    name: str
    email: str

    class Config:
        from_attributes = True


class TicketEnum(str, Enum):
    ACTIVE = "active"
    ERROR = "error"
    WARNING = "warning"
    ISSUE = "ISSUE"


class Ticket(pydantic.BaseModel):
    id: Optional[int] = -1
    status: TicketEnum = TicketEnum.ACTIVE
    text: str

    class Config:
        from_attributes = True


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class GenerateUserToken(pydantic.BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True


class GenerateOtp(pydantic.BaseModel):
    email: str


class VerifyOtp(pydantic.BaseModel):
    email: str
    otp: int


class BuyRequest(pydantic.BaseModel):
    payload: dict
    coin: str
    count: int


class ForgotPassword(pydantic.BaseModel):
    email: str


class ResetPassword(pydantic.BaseModel):
    email: str
    new_password: str
    repeat_password: str
    otp: int


class LoginRequest(pydantic.BaseModel):
    username: str
    password: str
