import datetime
import pydantic


class UserBase(pydantic.BaseModel):
    name: str
    email: str

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    username: str
    password: str

    class Config:
        from_attributes = True
        
class UserDelete(pydantic.BaseModel):
    email: str


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