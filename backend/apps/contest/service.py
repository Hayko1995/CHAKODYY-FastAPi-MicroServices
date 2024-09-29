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
from apps.auth.service import get_user_by_id, delete_user_by_id
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
    except Exception as e:
        print(e)
        return False


async def delete_contest(payload: dict, id: str, db: _orm.Session):

    user = await get_user_by_id(payload["id"], db)

    if user.is_admin:
        try:
            db.query(_models.Contest).filter(_models.Contest.id == id).delete()
            db.commit()
            return True
        except Exception as e:
            print(e)
            return False
    else:
        return False
    
async def get_contest(db: _orm.Session):
    try:
        return db.query(_models.Contest).all()
    except Exception as e:
        print(e)
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
        return "Server error"


async def remove_tickets(user_id, ticket: int, db: _orm.Session):
    try:
        user = await get_user_by_id(user_id, db)
        if ticket != -1:
            if user.is_admin:
                db.query(_models.Ticket).filter(_models.Ticket.id == ticket).delete()
                db.commit()
            return {"status": "sucsess"}

        else:
            return {"status": "unsucsess"}

    except Exception as e:
        print(e)
        return "Server  error"
