import fastapi
import sqlalchemy.orm as _orm
from apps.notification.email_service import notification
from apps.contest.schemas import CreateContest
from apps.auth.service import get_user_by_id
import db.models as _models
import datetime as _dt


async def create_contest(contest: CreateContest, db: _orm.Session):
    try:
        if (
            not db.query(_models.Contest)
            .filter(_models.Contest.title == contest.title)
            .first()
        ):
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
            db.flush()
            db.commit()
            db.refresh(contest)
            return contest
        else:
            {"status": "title already exists"}

    except Exception as e:
        print(e)
        return False


async def update_contest(contest: CreateContest, db: _orm.Session):
    try:
        if contest.id == -1:
            return fastapi.HTTPException(
                status_code=202,
                detail="Missing id ",
            )
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
            db.flush()
            db.commit()
            db.refresh(_, attribute_names=["id"])
        return _.id
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


async def join(user_id: int, id: int, db: _orm.Session):
    contest = get_contest_by_id(id, db)
    if get_contest_by_id(id, db) != None:

        if _dt.datetime.now() < contest.end_time:

            if await get_user_by_id(user_id, db) != None:
                try:
                    contest_participant = _models.ContestParticipant(
                        contest_id=id,
                        participant=user_id,
                        is_withdrawn=False,
                    )
                    db.add(contest_participant)
                    db.flush()
                    db.commit()
                    db.refresh(contest_participant)
                    return contest_participant
                except Exception as e:
                    print(e)
            else:
                return {"result": "no user"}
        else:
            return {"result": "ended"}
    else:
        return {"result": "no contest"}


async def exit(id: int, db: _orm.Session):
    try:
        contest_participant = (
            db.query(_models.ContestParticipant)
            .filter(_models.ContestParticipant.id == id)
            .first()
        )
        contest = (
            db.query(_models.Contest)
            .filter(_models.Contest.id == contest_participant.contest_id)
            .first()
        )

        if _dt.datetime.now() < contest.start_time:
            contest_participant.is_withdrawn = True
            contest_participant.withdraw_time = _dt.datetime.now()
            db.add(contest_participant)
            db.commit()
            return True
        else:
            return {"status": "you can't exit "}

    except Exception as e:
        print(e)
        return fastapi.HTTPException(
            status_code=500,
            detail="Server side error ",
        )


async def delete_participant(id: int, db: _orm.Session):
    try:
        (
            db.query(_models.ContestParticipant)
            .filter(_models.ContestParticipant.id == id)
            .delete()
        )
        db.commit()

    except Exception as e:
        print(e)
        return {"status": "Server Error"}
