import jwt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import email_validator as _email_check
import fastapi as _fastapi
import fastapi.security as _security
from passlib.hash import pbkdf2_sha256
from apps.notification.email_service import notification
from apps.support.schemas import Ticket
from apps.auth.service import get_user_by_id
import db.database as database
import apps.auth.schemas as _schemas
import db.models as _models


def verefy_user(user: _models.User, db: _orm.Session):
    user.is_verified = True
    db.commit()


async def create_ticket(user_id, ticket: Ticket, db: _orm.Session):
    try:
        if ticket.id == -1:
            ticket_obj = _models.Ticket(
                text=ticket.text, user_id=user_id, 
                status=ticket.status, request_type=ticket.request_type
            )
            db.add(ticket_obj)
            db.commit()
        else:
            ticket_obj = (
                db.query(_models.Ticket)
                .filter(
                    _models.Ticket.id == ticket.id and _models.Ticket.user_id == user_id
                )
                .first()
            )
            ticket_obj.status = ticket.status
            ticket_obj.text = ticket.text
            ticket_obj.request_type = ticket.request_type

            db.add(ticket_obj)
            db.commit()
        return True
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
                model = (
                    db.query(_models.Ticket).filter(_models.Ticket.id == ticket).first()
                )
                model.status = "resolved"
                db.commit()
            return {"status": "sucsess"}

        else:
            return {"status": "unsucsess"}

    except Exception as e:
        print(e)
        return "Server error"
