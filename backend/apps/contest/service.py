import jwt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import email_validator as _email_check
import fastapi as _fastapi
import fastapi.security as _security
from passlib.hash import pbkdf2_sha256
from apps.notification.email_service import notification
from apps.support.schemas import Ticket
from apps.contest.schemas import CreateContest
import db.database as database
import apps.auth.schemas as _schemas
import db.models as _models
import random
import json
import pika
import time
import os




async def create_contest(contest: CreateContest, db: _orm.Session):
    try:
        if contest.id == -1:
            contest = _models.Contest(
                title=contest.title,
                category=contest.category,
                start_time=contest.start_time,
                end_time=contest.end_time,
                reward=contest.reward,
                contest_coins=contest.contest_coins,
                trading_balance=contest.trading_balance,
            )
            db.add(contest)
            db.commit()
        else:
            _ = (
                db.query(_models.Contest)
                .filter(_models.Contest.id == contest.id)
                .first()
            )
            _.title = contest.title
            _.category = contest.category
            _.start_time = contest.start_time
            _.end_time = contest.end_time
            _.reward = contest.reward
            _.contest_coins = contest.contest_coins
            _.trading_balance = (contest.trading_balance,)

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
