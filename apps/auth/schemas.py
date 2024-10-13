import datetime
from typing import Optional
import pydantic


class UserBase(pydantic.BaseModel):
    name: str
    email: str

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    username: str
    password: str
    address: Optional[str]
    street: Optional[str]
    state: Optional[str]
    city: Optional[str]
    country: Optional[str]
    pincode: Optional[str]
    nationality: Optional[str]
    preference_timezone: Optional[str]
    preference_language: Optional[str]
    preference_login_method: Optional[str]
    phone_number: Optional[str]
        
    class Config:
        from_attributes = True

class UpdateUser(pydantic.BaseModel):
    address: Optional[str]
    street: Optional[str]
    state: Optional[str]
    city: Optional[str]
    country: Optional[str]
    pincode: Optional[str]
    nationality: Optional[str]
    preference_timezone: Optional[str]
    preference_language: Optional[str]
    preference_login_method: Optional[str]
    phone_number: Optional[str]
        
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
