import jwt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import email_validator as _email_check
import fastapi as _fastapi
import fastapi.security as _security
from passlib.hash import pbkdf2_sha256
from apps.notification.email_service import notification
from apps.support.schemas import Ticket
import db.database as _database
import apps.auth.schemas as _schemas
import db.models as _models
import random
import json
import pika
import time
import os


def create_database():
    # Create database tables
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    # Dependency to get a database session
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()



def verefy_user(user: _models.User, db: _orm.Session):
    user.is_verified = True
    db.commit()


async def create_ticket(user_id, ticket: Ticket, db: _orm.Session):
    ticket = _models.Ticket(text=ticket.text, user_id=user_id, status=ticket.status)
    db.add(ticket)
    db.commit()
    return db.query(_models.Ticket).filter(_models.User.id == id).first()


async def get_user_by_id(id: int, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.id == id).first()


async def delete_user_by_id(id: int, db: _orm.Session):
    # Retrieve a user by email from the database

    db.query(_models.User).filter(_models.User.id == id).delete()
    db.commit()



