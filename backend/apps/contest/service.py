import jwt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import email_validator as _email_check
import fastapi as _fastapi
import fastapi.security as _security
from passlib.hash import pbkdf2_sha256
from apps.notification.email_service import notification
from apps.support.schemas import Ticket
from apps.contest.schemas import CreateContest, Join
from apps.auth.service import get_user_by_id, delete_user_by_id
import db.database as database
import apps.auth.schemas as _schemas
import db.models as _models
import random
import json
import pika
import time
import os
import datetime as _dt


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


def get_contest_by_id(id: int, db: _orm.Session):
    return db.query(_models.Contest).filter(_models.Contest.id == id).first()


async def join(id: int, join: Join, db: _orm.Session):
    if get_contest_by_id(join.contest_id, db) != None:
        if await get_user_by_id(id, db) != None:
            try:
                contest_participant = _models.ContestParticipant(
                    contest_id=join.contest_id,
                    participant=id,
                    is_withdrawn=False,
                )
                db.add(contest_participant)
                db.commit()
                return True
            except Exception as e:
                print(e)
        else:
            return {"result": "no user"}
    else:
        return {"result": "no contest"}


async def exit(id: int, db: _orm.Session):
    try:
        contest_participant = (
            db.query(_models.ContestParticipant)
            .filter(_models.ContestParticipant.id == id)
            .first()
        )
        contest_participant.withdraw_time = _dt.datetime.now()
        db.add(contest_participant)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False
