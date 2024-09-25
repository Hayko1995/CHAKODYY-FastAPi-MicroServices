import logging
import os
from typing import Any
from fastapi import Depends, HTTPException
from fastapi import security
import pika
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import fastapi
from fastapi import BackgroundTasks
import uvicorn
import sqlalchemy.orm as orm


from apps.auth import schemas
import apps.auth.service as _services

from datetime import datetime

from email_validator import validate_email, EmailNotValidError

from apps.converter.routing.converter import jwt_validation
from db import models


auth = fastapi.APIRouter(prefix="/auth", tags=["auth"])
oauth2schema = security.OAuth2PasswordBearer("/auth/token")


@auth.post("/api/users")
async def create_user(
    user: schemas.UserCreate, db: orm.Session = fastapi.Depends(_services.get_db)
):
    db_user = await _services.get_user_by_email(email=user.email, db=db)

    if db_user:
        logging.info("User with that email already exists")
        raise fastapi.HTTPException(
            status_code=200, detail="User with that email already exists"
        )

    user = await _services.create_user(user=user, db=db)

    return fastapi.HTTPException(
        status_code=201,
        detail="User Registered, Please verify email to activate account !",
    )


@auth.post("/api/super_users")
async def create_user(
    user: schemas.UserCreate, db: orm.Session = fastapi.Depends(_services.get_db)
):
    db_user = await _services.get_user_by_email(email=user.email, db=db)

    if db_user:
        logging.info("User with that email already exists")
        raise fastapi.HTTPException(
            status_code=200, detail="User with that email already exists"
        )

    user = await _services.create_super_user(user=user, db=db)

    return fastapi.HTTPException(
        status_code=201,
        detail="User Registered, Please verify email to activate account !",
    )


@auth.post("/api/delete_user")  # todo chenage to JWT verefication
async def delete_user(
    db: orm.Session = fastapi.Depends(_services.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    await _services.delete_user_by_id(id=payload['id'], db=db)

    return fastapi.HTTPException(
        status_code=200,
        detail="User Registered, Please verify email to activate account !",
    )


# Endpoint to check if the API is live
@auth.get("/check_api")
async def check_api():
    return {"status": "Connected to API Successfully"}


@auth.post("/token")  # marge with "/api/token"
async def swagger_login(
    user_data: OAuth2PasswordRequestForm = Depends(),
    db: orm.Session = fastapi.Depends(_services.get_db),
) -> Any:

    try:
        emailinfo = validate_email(user_data.username, check_deliverability=False)
        email = emailinfo.normalized

    except EmailNotValidError as e:

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
        raise fastapi.HTTPException(
            status_code=403,
            detail="Email verification is pending. Please verify your email to proceed.",
        )

    if not user:
        logging.info("Invalid Credentials")
        raise fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    logging.info("JWT Token Generated")

    return await _services.create_token(user=user)


@auth.post("/api/token")
async def generate_token(
    # form_data: _security.OAuth2PasswordRequestForm = fastapi.Depends(),
    user_data: schemas.GenerateUserToken,
    db: orm.Session = fastapi.Depends(_services.get_db),
):

    try:
        emailinfo = validate_email(user_data.username, check_deliverability=False)
        email = emailinfo.normalized

    except EmailNotValidError as e:

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
        raise fastapi.HTTPException(
            status_code=403,
            detail="Email verification is pending. Please verify your email to proceed.",
        )

    if not user:
        logging.info("Invalid Credentials")
        raise fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    logging.info("JWT Token Generated")
    return await _services.create_token(user=user)


@auth.get("/api/users/me", response_model=schemas.User, tags=["User Auth"])
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
    db: orm.Session = fastapi.Depends(_services.get_db),
):
    user = await _services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        raise fastapi.HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise fastapi.HTTPException(status_code=400, detail="User is already verified")

    # Generate and send OTP
    otp = _services.generate_otp()

    background_tasks.add_task(_services.send_otp, userdata.email, otp)
    # _services.send_otp(userdata.email, otp, channel) //todo change

    # Store the OTP in the database
    user.otp = otp
    user.otp_created_at = datetime.now()
    db.add(user)
    db.commit()

    return "OTP sent to your email"


@auth.post("/api/users/verify_otp")
async def verify_otp(
    userdata: schemas.VerifyOtp, db: orm.Session = fastapi.Depends(_services.get_db)
):
    user = await _services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        raise fastapi.HTTPException(status_code=404, detail="User not found")

    if not user.otp or user.otp != userdata.otp:
        raise fastapi.HTTPException(status_code=400, detail="Invalid OTP")

    # OTP expiration check.
    otp_duration = datetime.now() - user.otp_created_at
    total_time_difference = otp_duration.total_seconds() / 60  # Difference by minutes.

    otp_expiration_minutes = float(os.environ.get("OTP_EXPIRATION_TIME_MINUTES"))
    if total_time_difference > otp_expiration_minutes:
        raise fastapi.HTTPException(
            status_code=400, detail="OTP expired. Generate a new OTP and try again."
        )

    # Update user's is_verified field
    user.is_verified = True
    user.otp = None  # Clear the OTP
    db.add(user)
    db.commit()

    return "Email verified successfully"


@auth.post("/api/users/forgot_password")  # add Test
async def forgot_password(
    userdata: schemas.ForgotPassword,
    db: orm.Session = fastapi.Depends(_services.get_db),
):
    user = await _services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        raise fastapi.HTTPException(status_code=404, detail="User not found")

    # Generate and send OTP
    otp = _services.generate_otp()

    # _services.send_otp(userdata.email, otp, channel) //todo change

    # Store the OTP in the database
    user.otp = otp
    user.otp_created_at = datetime.now()
    db.add(user)
    db.commit()

    return "OTP was sent to the user's email."


@auth.post("/api/users/reset_password")  # add Test
async def reset_password(
    userdata: schemas.ResetPassword,
    db: orm.Session = fastapi.Depends(_services.get_db),
):
    user = await _services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        raise fastapi.HTTPException(status_code=404, detail="User not found")

    # Verify OTP
    if (
        not user.otp or user.otp != userdata.otp
    ):  # todo add here created time compare to now time  if it is greater than 30 mins ingore otp
        raise fastapi.HTTPException(status_code=400, detail="Invalid OTP")

    # OTP expiration check.
    otp_duration = datetime.now() - user.otp_created_at
    total_time_difference = otp_duration.total_seconds() / 60  # Difference by minutes.

    otp_expiration_minutes = float(os.environ.get("OTP_EXPIRATION_TIME_MINUTES"))
    if total_time_difference > otp_expiration_minutes:
        raise fastapi.HTTPException(
            status_code=400, detail="OTP expired. Generate a new OTP and try again."
        )

    if userdata.new_password != userdata.repeat_password:
        raise fastapi.HTTPException(status_code=400, detail="Passwords do not match")

    # Update password in the database.
    user.hashed_password = userdata.new_password
    db.add(user)
    db.commit()

    return "OTP was sent to the user's email."
