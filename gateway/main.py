from typing import Any
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
import fastapi as _fastapi
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
from jwt.exceptions import DecodeError
from pydantic import BaseModel
import requests
import base64
import pika
import logging
import os
import jwt
import rpc_client

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Retrieve environment variables
JWT_SECRET = os.environ.get("JWT_SECRET")
AUTH_BASE_URL = os.environ.get("AUTH_BASE_URL")
CONVERTER_BASE_URL = os.environ.get("CONVERTER_BASE_URL")
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")

# Connect to RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBITMQ_URL)
)  # add container name in docker
channel = connection.channel()
channel.queue_declare(queue="gatewayservice")
channel.queue_declare(queue="ocr_service")


# JWT token validation
async def jwt_validation(token: str = _fastapi.Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except DecodeError:
        raise HTTPException(status_code=401, detail="Invalid JWT token")


# Pydantic models for request body
class GenerateUserToken(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ConvertRequest(BaseModel):
    from_coin: str
    to_coin: str
    count_coin: str
    price_coin: str


class BuyRequest(BaseModel):
    coinmname: str
    count: str


class UserRegisteration(BaseModel):
    name: str
    email: str
    password: str


class GenerateOtp(BaseModel):
    email: str


class VerifyOtp(BaseModel):
    email: str
    otp: int


async def login_auth(data):
    try:
        response = requests.post(
            f"{AUTH_BASE_URL}/api/token",
            json={"username": data.username, "password": data.password},
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503, detail="Authentication service is unavailable"
        )


@app.post("/token")
async def swagger_login(user_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    await login_auth(user_data)


# Authentication routes
@app.post("/auth/login", tags=["Authentication Service"])
async def login(user_data: OAuth2PasswordRequestForm = Depends()):
    await login_auth(user_data)


@app.post("/auth/register", tags=["Authentication Service"])
async def registeration(user_data: UserRegisteration):
    try:
        response = requests.post(
            f"{AUTH_BASE_URL}/api/users",
            json={
                "name": user_data.name,
                "email": user_data.email,
                "password": user_data.password,
            },
        )
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503, detail="Authentication service is unavailable"
        )


@app.post("/auth/generate_otp", tags=["Authentication Service"])
async def generate_otp(user_data: GenerateOtp):
    try:
        response = requests.post(
            f"{AUTH_BASE_URL}/api/users/generate_otp", json={"email": user_data.email}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503, detail="Authentication service is unavailable"
        )


@app.post("/auth/verify_otp", tags=["Authentication Service"])
async def verify_otp(user_data: VerifyOtp):
    try:
        response = requests.post(
            f"{AUTH_BASE_URL}/api/users/verify_otp",
            json={"email": user_data.email, "otp": user_data.otp},
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503, detail="Authentication service is unavailable"
        )


# Buy coins
@app.post("/conver/buy", tags=["Convet Money"])
def buy_coins(request: BuyRequest, payload: dict = _fastapi.Depends(jwt_validation)):
    try:
        response = requests.post(
            f"{CONVERTER_BASE_URL}/api/buy",
            json={
                "payload": payload,
                "from_coin": request.from_coin,
                "to_coin": request.to_coin,
                "price_coin": request.price_coin,
                "": request.count_coin,
            },
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503, detail="Authentication service is unavailable"
        )


# convert coins
@app.post("/conver/convert", tags=["Convet Money"])
def convert_coins(
    request: ConvertRequest, payload: dict = _fastapi.Depends(jwt_validation)
):
    try:
        response = requests.post(
            f"{CONVERTER_BASE_URL}/api/convert",
            json={
                "payload": payload,
                "from_coin": request.from_coin,
                "to_coin": request.to_coin,
                "price_coin": request.price_coin,
                "count_coin": request.count_coin,
            },
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503, detail="Authentication service is unavailable"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
