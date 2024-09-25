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
    try:
        if ticket.id == -1:
            print(
                "🐍 File: support/service.py | Line: 42 | undefined ~ ticket.id",
                ticket.id,
            )
            print("//////////////////")
            ticket = _models.Ticket(
                text=ticket.text, user_id=user_id, status=ticket.status
            )
            db.add(ticket)
            db.commit()
        else:
            _ = (
                db.query(_models.Ticket)
                .filter(
                    _models.Ticket.id == ticket.id and _models.Ticket.user_id == user_id
                )
                .first()
            )
            _.status = ticket.status
            _.text = ticket.text
            db.add(_)
            db.commit()
        return True
    except:
        return False


async def get_tickets(user_id, ticket: int, db: _orm.Session):
    try:
        user = await get_user_by_id(user_id, db)
        if ticket == -1:
            if user.is_admin:
                return db.query(_models.Ticket).all()
            return (
                db.query(_models.Ticket)
                .filter(_models.Ticket.user_id == str(user_id))
                .all()
            )

        else:
            print(ticket)
            res = (
                db.query(_models.Ticket)
                .filter(
                    _models.Ticket.user_id == str(user_id), _models.Ticket.id == ticket
                )
                .first()
            )
            return [res]

    except Exception as e:
        print(e)
        raise "Server error"


async def remove_tickets(user_id, ticket: int, db: _orm.Session):
    try:
        user = await get_user_by_id(user_id, db)
        if not ticket == -1:
            if user.is_admin:
                db.query(_models.Ticket).filter(_models.Ticket.id == ticket).delete()
                db.commit()
            return {"status": "sucsess"}

        else:
            return {"status": "unsucsess"}

    except Exception as e:
        print(e)
        raise "Server error"


async def get_user_by_id(id: int, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.id == id).first()


async def delete_user_by_id(id: int, db: _orm.Session):
    # Retrieve a user by email from the database

    db.query(_models.User).filter(_models.User.id == id).delete()
    db.commit()
