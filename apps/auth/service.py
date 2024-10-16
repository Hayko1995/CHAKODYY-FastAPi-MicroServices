import jwt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import email_validator as _email_check
import fastapi as _fastapi
import fastapi.security as _security
from passlib.hash import pbkdf2_sha256
from apps.notification.email_service import notification
import db.database as _database
import apps.auth.schemas as _schemas
import db.models as _models
import random
import json
import pika
import time
import os

# Load environment variables
JWT_SECRET = os.getenv("JWT_SECRET")
oauth2schema = _security.OAuth2PasswordBearer("/auth/token")


def create_database():
    # Create database tables
    return _database.Base.metadata.create_all(bind=_database.engine)


async def get_user_by_email(email: str, db: _orm.Session):
    # Retrieve a user by email from the database
    return (
        db.query(_models.User)
        .filter(_models.User.email == email and _models.User.is_verified == True)
        .first()
    )


def get_user_by_email_hard(email: str, db: _orm.Session):
    # Retrieve a user by email from the database
    return db.query(_models.User).filter(_models.User.email == email).first()


def verify_user(user: _models.User, db: _orm.Session):
    user.is_verified = True
    db.commit()


async def delete_user_by_id(id: int, db: _orm.Session):
    # Retrieve a user by email from the database

    db.query(_models.User).filter(_models.User.id == id).delete()
    db.commit()


async def create_user(user: _schemas.UserCreate, db: _orm.Session):
    # Create a new user in the database
    try:
        valid = _email_check.validate_email(user.email)
        name = user.name
        username = user.username
        email = valid.email
    except _email_check.EmailNotValidError:
        raise _fastapi.HTTPException(
            status_code=404, detail="Please enter a valid email"
        )

    user_obj = _models.User(
        email=email,
        username=username,
        name=name,
        hashed_password=pbkdf2_sha256.hash(user.password),
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def update_user(update_data: _schemas.UpdateUser, id: int, db: _orm.Session):

    try:
        user = await get_user_by_id(id=id, db=db)
        user.address = update_data.address
        user.street = update_data.street
        user.state = update_data.state
        user.city = update_data.city
        user.country = update_data.country
        user.pincode = update_data.pincode
        user.nationality = update_data.nationality
        user.preference_timezone = update_data.preference_timezone
        user.preference_language = update_data.preference_language
        user.preference_login_method = update_data.preference_login_method

        db.commit()
        db.refresh(user)
        return user

    except _email_check.EmailNotValidError:
        raise _fastapi.HTTPException(
            status_code=404, detail="Please enter a valid email"
        )

    user_obj = _models.User(
        email=email,
        username=username,
        name=name,
        hashed_password=pbkdf2_sha256.hash(user.password),
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def create_super_user(user: _schemas.UserCreate, db: _orm.Session):
    # Create a new user in the database
    try:
        valid = _email_check.validate_email(user.email)
        name = user.name
        username = user.username
        email = valid.email
    except _email_check.EmailNotValidError:
        raise _fastapi.HTTPException(
            status_code=404, detail="Please enter a valid email"
        )

    user_obj = _models.User(
        email=email,
        username=username,
        name=name,
        is_verified=True,
        is_admin=True,
        hashed_password=pbkdf2_sha256.hash(user.password),
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(email: str, password: str, db: _orm.Session):
    # Authenticate a user
    user = await get_user_by_email(email=email, db=db)

    if not user:
        return False

    if not user.is_verified:
        return "is_verified_false"

    if not user.verify_password(password):
        return False

    return user


async def create_token(user: _models.User):
    # Create a JWT token for authentication
    user_obj = _schemas.User.from_orm(user)
    user_dict = user_obj.model_dump()
    token = jwt.encode(user_dict, JWT_SECRET, algorithm="HS256")
    return dict(access_token=token, token_type="bearer")


async def get_current_user(
    db: _orm.Session = _fastapi.Depends(_database.get_db),
    token: str = _fastapi.Depends(oauth2schema),
):
    # Get the current authenticated user from the JWT token
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
    except Exception as e:
        print(e)
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid Email or Password"
        )
    return _schemas.User.from_orm(user)


def generate_otp():
    # Generate a random OTP
    return str(random.randint(100000, 999999))  # change to time tocken


def send_otp(email, otp):
    # Send an OTP email notification
    message = {
        "email": email,
        "subject": "Account Verification OTP Notification",
        "other": "null",
        "body": f"Your OTP for account verification is: {otp} \n Please enter this OTP on the verification page to complete your account setup. \n If you did not request this OTP, please ignore this message.\n Thank you ",
    }

    try:
        notification(message)
        print("Sent OTP email notification")
    except Exception as err:
        print(f"Failed to publish message: {err}")


async def get_user_by_id(id: int, db: _orm.Session):
    try:
        res = db.query(_models.User).filter(_models.User.id == id).first()
        return res
    except Exception as e:
        print(e)
        return None


async def delete_user_by_id(id: int, db: _orm.Session):
    # Retrieve a user by email from the database

    db.query(_models.User).filter(_models.User.id == id).delete()
    db.commit()
