import logging
import os
import pika

import fastapi as _fastapi
import uvicorn
import sqlalchemy.orm as _orm

import database as _database
import models as _models
import schemas as _schemas
import service as _services

from datetime import datetime

from email_validator import validate_email, EmailNotValidError


# rabbitmq connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=os.getenv("RABBITMQ_URL"))
)
channel = connection.channel()
channel.queue_declare(queue="email_notification")


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = _fastapi.FastAPI()
logging.basicConfig(level=logging.INFO)
_models.Base.metadata.create_all(_models.engine)


@app.post("/api/users", tags=["User Auth"])
async def create_user(
    user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    db_user = await _services.get_user_by_email(email=user.email, db=db)

    if db_user:
        logging.info("User with that email already exists")
        raise _fastapi.HTTPException(
            status_code=200, detail="User with that email already exists"
        )

    user = await _services.create_user(user=user, db=db)

    return _fastapi.HTTPException(
        status_code=201,
        detail="User Registered, Please verify email to activate account !",
    )


# Endpoint to check if the API is live
@app.get("/check_api")
async def check_api():
    return {"status": "Connected to API Successfully"}


@app.post("/api/token", tags=["User Auth"])
async def generate_token(
    # form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
    user_data: _schemas.GenerateUserToken,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):

    try:
        emailinfo = validate_email(user_data.username, check_deliverability=False)
        email = emailinfo.normalized

    except EmailNotValidError as e:

        email = (
            db.query(_models.User).filter_by(username=user_data.username).first().email
        )

    user = await _services.authenticate_user(
        email=email, password=user_data.password, db=db
    )

    if user == "is_verified_false":
        logging.info(
            "Email verification is pending. Please verify your email to proceed. "
        )
        raise _fastapi.HTTPException(
            status_code=403,
            detail="Email verification is pending. Please verify your email to proceed.",
        )

    if not user:
        logging.info("Invalid Credentials")
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    logging.info("JWT Token Generated")
    return await _services.create_token(user=user)


@app.get("/api/users/me", response_model=_schemas.User, tags=["User Auth"])
async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user


@app.get("/api/users/profile", tags=["User Auth"])
async def get_user(email: str, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return db.query(_models.User).filter_by(id=1).first()


@app.post("/api/users/generate_otp", response_model=str, tags=["User Auth"])
async def send_otp_mail(
    userdata: _schemas.GenerateOtp,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    user = await _services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        raise _fastapi.HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise _fastapi.HTTPException(status_code=400, detail="User is already verified")

    # Generate and send OTP
    otp = _services.generate_otp()
    
    _services.send_otp(userdata.email, otp, channel)

    # Store the OTP in the database
    user.otp = otp
    user.otp_created_at = datetime.now()
    db.add(user)
    db.commit()

    return "OTP sent to your email"


@app.post("/api/users/verify_otp", tags=["User Auth"])
async def verify_otp(
    userdata: _schemas.VerifyOtp, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    user = await _services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        raise _fastapi.HTTPException(status_code=404, detail="User not found")

    if not user.otp or user.otp != userdata.otp:
        raise _fastapi.HTTPException(status_code=400, detail="Invalid OTP")
    
    # OTP expiration check.
    otp_duration = datetime.now() - user.otp_created_at
    total_time_difference = otp_duration.total_seconds() / 60  # Difference by minutes.

    otp_expiration_minutes = float(os.environ.get("OTP_EXPIRATION_TIME_MINUTES"))
    if total_time_difference > otp_expiration_minutes:
        raise _fastapi.HTTPException(status_code=400, detail="OTP expired. Generate a new OTP and try again.")

    # Update user's is_verified field
    user.is_verified = True
    user.otp = None  # Clear the OTP
    db.add(user)
    db.commit()

    return "Email verified successfully"


@app.post("/api/users/forgot_password", tags=["User Auth"])
async def forgot_password(
    userdata: _schemas.ForgotPassword, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    user = await _services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        raise _fastapi.HTTPException(status_code=404, detail="User not found")
    
    # Generate and send OTP
    otp = _services.generate_otp()
    
    _services.send_otp(userdata.email, otp, channel)

    # Store the OTP in the database
    user.otp = otp
    user.otp_created_at = datetime.now()
    db.add(user)
    db.commit()

    return "OTP was sent to the user's email."


@app.post("/api/users/reset_password", tags=["User Auth"])
async def reset_password(
    userdata: _schemas.ResetPassword, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    user = await _services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        raise _fastapi.HTTPException(status_code=404, detail="User not found")
    
    # Verify OTP
    if not user.otp or user.otp != userdata.otp:  #todo add here created time compare to now time  if it is greater than 30 mins ingore otp 
        raise _fastapi.HTTPException(status_code=400, detail="Invalid OTP")
    
    # OTP expiration check.
    otp_duration = datetime.now() - user.otp_created_at
    total_time_difference = otp_duration.total_seconds() / 60  # Difference by minutes.

    otp_expiration_minutes = float(os.environ.get("OTP_EXPIRATION_TIME_MINUTES"))
    if total_time_difference > otp_expiration_minutes:
        raise _fastapi.HTTPException(status_code=400, detail="OTP expired. Generate a new OTP and try again.")
    
    if userdata.new_password != userdata.repeat_password:
        raise _fastapi.HTTPException(status_code=400, detail="Passwords do not match")

    # Update password in the database.
    user.hashed_password = userdata.new_password
    db.add(user)
    db.commit()

    return "OTP was sent to the user's email."


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
