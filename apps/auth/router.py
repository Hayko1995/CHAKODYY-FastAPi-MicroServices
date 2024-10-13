import logging
import jwt
import os

import fastapi
import sqlalchemy.orm as orm

import apps.auth.service as _services
import db.database as database

from datetime import datetime
from passlib.hash import pbkdf2_sha256

from email_validator import validate_email, EmailNotValidError
from fastapi import BackgroundTasks, Depends, HTTPException, security, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Any

from apps.auth import schemas
from db import models

auth = fastapi.APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = security.OAuth2PasswordBearer("/auth/token")


JWT_SECRET = os.getenv("JWT_SECRET")


async def jwt_validation(token: str = fastapi.Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except UnicodeError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content="Invalid JWT token"
        )


@auth.post("/api/users")
async def create_user(
    user: schemas.UserCreate, db: orm.Session = fastapi.Depends(database.get_db)
):
    user.email = user.email.lower()
    db_user = await _services.get_user_by_email(email=user.email, db=db)

    if db_user:
        logging.info("User with the given email already exists")
        data = {"message": "User with the given email already exists"}
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=data)

    user = await _services.create_user(user=user, db=db)

    data = {"message": "User registered. Please verify email to activate your account!"}
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)


@auth.put("/api/users")
async def update_user(
    update_data: schemas.UpdateUser,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):

    user = await _services.update_user(update_data, id=payload["id"], db=db)

    data = {"message": "Updated "}
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@auth.post("/api/super_users")
async def create_user(
    user: schemas.UserCreate, db: orm.Session = fastapi.Depends(database.get_db)
):
    user.email = user.email.lower()
    db_user = await _services.get_user_by_email(email=user.email, db=db)

    if db_user:
        logging.info("User with that email already exists")
        raise fastapi.HTTPException(
            status_code=200, detail="User with that email already exists"
        )

    user = await _services.create_super_user(user=user, db=db)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content="User Registered, Please verify email to activate account !",
    )


@auth.post("/api/delete_user")
async def delete_user(
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    await _services.delete_user_by_id(id=payload["id"], db=db)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="User Deleted",
    )


# Endpoint to check if the API is live
@auth.get("/check_api")
async def check_api():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Connected to API Successfully",
    )


@auth.post("/token")  # marge with "/api/token"
async def swagger_login(
    user_data: OAuth2PasswordRequestForm = Depends(),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> Any:

    try:
        emailinfo = validate_email(user_data.username, check_deliverability=False)
        email = emailinfo.normalized

    except EmailNotValidError as e:
        print(e)
        email = (
            db.query(models.User).filter_by(username=user_data.username).first().email
        )

    user = await _services.authenticate_user(
        email=email, password=user_data.password, db=db
    )

    if user == "is_verified_false":
        logging.info(
            "Email verification is pending. Please verify your email to proceed. "
        )

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content="Email verification is pending. Please verify your email to proceed.",
        )

    if not user:
        logging.info("Invalid  Credentials")
        raise fastapi.HTTPException(status_code=401, detail="Invalid  Credentials")

    logging.info("JWT Token Generated")

    return await _services.create_token(user=user)


@auth.post("/api/token")
async def generate_token(
    # form_data: _security.OAuth2PasswordRequestForm = fastapi.Depends(),
    user_data: schemas.GenerateUserToken,
    db: orm.Session = fastapi.Depends(database.get_db),
):

    try:
        emailinfo = validate_email(user_data.username, check_deliverability=False)
        email = emailinfo.normalized

    except EmailNotValidError as e:
        print(e)
        email = (
            db.query(models.User).filter_by(username=user_data.username).first().email
        )

    user = await _services.authenticate_user(
        email=email, password=user_data.password, db=db
    )

    if user == "is_verified_false":
        logging.info(
            "Email verification is pending. Please verify your email to proceed. "
        )
        data = {
            "message": "Email verification is pending. Please verify your email to proceed."
        }
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=data)

    if not user:
        logging.info("Invalid Credentials")
        data = {"message": "Invalid Credentials"}
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

    logging.info("JWT Token Generated")
    access_token = await _services.create_token(user=user)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=access_token)


@auth.get("/api/users/me", response_model=schemas.User)
async def get_user(user: schemas.User = fastapi.Depends(_services.get_current_user)):
    return user


def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)


@auth.post("/api/users/generate_otp", response_model=str)
async def send_otp_mail(
    userdata: schemas.GenerateOtp,
    background_tasks: BackgroundTasks,
    db: orm.Session = fastapi.Depends(database.get_db),
):
    user = await _services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        data = {"message": "User not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)

    if user.is_verified:
        data = {"message": "The user is already verified"}
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=data)

    # Generate and send OTP
    otp = _services.generate_otp()

    background_tasks.add_task(_services.send_otp, userdata.email, otp)

    # Store the OTP in the database
    user.otp = otp
    user.otp_created_at = datetime.now()
    db.add(user)
    db.commit()

    data = {"message": "The OTP has been sent to your email address"}
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@auth.post("/api/users/verify_otp")
async def verify_otp(
    userdata: schemas.VerifyOtp, db: orm.Session = fastapi.Depends(database.get_db)
):
    user = await _services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        data = {"message": "User not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)

    if not user.otp or user.otp != userdata.otp:
        data = {"message": "Invalid OTP"}
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

    # OTP expiration check.
    otp_duration = datetime.now() - user.otp_created_at
    total_time_difference = otp_duration.total_seconds() / 60  # Difference by minutes.

    otp_expiration_minutes = float(os.environ.get("OTP_EXPIRATION_TIME_MINUTES"))
    if total_time_difference > otp_expiration_minutes:
        data = {
            "message": "The OTP has been expired. Generate a new OTP and try again."
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

    # Update user's is_verified field
    user.is_verified = True
    user.otp = None  # Clear the OTP
    db.add(user)
    db.commit()

    data = {"message": "The email address is verified successfully"}
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@auth.post("/api/users/forgot_password")  # add Test
async def forgot_password(
    userdata: schemas.ForgotPassword,
    background_tasks: BackgroundTasks,
    db: orm.Session = fastapi.Depends(database.get_db),
):
    user = await _services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        data = {"message": "User not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)

    # Generate and send OTP
    otp = _services.generate_otp()

    background_tasks.add_task(_services.send_otp, userdata.email, otp)

    # Store the OTP in the database
    user.otp = otp
    user.otp_created_at = datetime.now()
    db.add(user)
    db.commit()

    data = {"message": "The OTP has been sent to your email address"}
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@auth.post("/api/users/reset_password")  # add Test
async def reset_password(
    userdata: schemas.ResetPassword,
    db: orm.Session = fastapi.Depends(database.get_db),
):
    user = await _services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        data = {"message": "User not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)

    # Verify OTP
    if not user.otp or user.otp != userdata.otp:
        data = {"message": "Invalid OTP"}
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

    # OTP expiration check.
    otp_duration = datetime.now() - user.otp_created_at
    total_time_difference = otp_duration.total_seconds() / 60  # Difference by minutes.

    otp_expiration_minutes = float(os.environ.get("OTP_EXPIRATION_TIME_MINUTES"))
    if total_time_difference > otp_expiration_minutes:
        data = {
            "message": "The OTP has been expired. Generate a new OTP and try again."
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

    if userdata.new_password != userdata.repeat_password:
        data = {"message": "Passwords do not match"}
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

    # Update password in the database.
    user.hashed_password = pbkdf2_sha256.hash(userdata.new_password)
    db.add(user)
    db.commit()

    data = {"message": "Password is reset successfully"}
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)
