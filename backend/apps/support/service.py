import json

import db.models as _models
import sqlalchemy.orm as _orm

from apps.auth.service import get_user_by_id
from apps.support.schemas import CreateTicketRequest, TicketEnum, UpdateTicketRequest
from datetime import datetime


def format_with_fstring(number, length=5):
    return f"{number:0{length}}"


async def create_ticket(user_id, ticket: CreateTicketRequest, db: _orm.Session):
    try:
        try:
            obj = db.query(_models.Ticket).order_by(_models.Ticket.id.desc()).first()
            _id = obj.id
        except Exception as e:
            _id = 0

        ticket_obj = _models.Ticket(
            ticket_number=f"{datetime.today().date().strftime('%Y%m%d')}-{format_with_fstring(_id+1)}",
            text=ticket.text,
            user_id=user_id,
            status=ticket.status,
            request_type=ticket.request_type,
        )

        ticket_history = _models.Ticket_history(
            ticket_number=f"{datetime.today().date().strftime('%Y%m%d')}-{format_with_fstring(_id+1)}",
            ticket_message=ticket.text,
            created_by=user_id,
        )
        db.add(ticket_obj)
        db.add(ticket_history)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False


async def update_ticket(user_id, ticket: UpdateTicketRequest, db: _orm.Session):
    try:
        # Verify user.
        user = await get_user_by_id(user_id, db)
        if user == None:
            return "User not found"

        try:
            ticket_obj = (
                db.query(_models.Ticket)
                .filter(
                    _models.Ticket.id == ticket.id and _models.Ticket.user_id == user_id
                )
                .first()
            )

            ticket_obj.status = ticket.status
            ticket_obj.request_type = ticket.request_type
            ticket_obj.action_owner = ticket.action_owner
            ticket_obj.subject = ticket.subject

            ticket_history = _models.Ticket_history(
                ticket_number=ticket_obj.ticket_number,
                ticket_message=ticket.subject,
                created_by=user_id,
            )

            db.add(ticket_obj)
            db.add(ticket_history)
            db.commit()
            return "success"
        except Exception as e:
            print(e)
            return "Ticket not found"
    except Exception as e:
        print(e)
        return False


async def get_ticket(user_id, ticket_id: int, db: _orm.Session):
    try:
        # Verify user.
        user = await get_user_by_id(user_id, db)
        if user == None:
            return "User not found"

        try:
            if user.is_admin:
                res = (
                    db.query(_models.Ticket).all()
                )
                return res
            res = (
                db.query(_models.Ticket)
                .filter(
                    _models.Ticket.user_id == str(user_id),
                    _models.Ticket.id == ticket_id,
                )
                .first()
            )
            res_data = {
                "id": res.id,
                "text": res.text,
                "status": res.status,
                "request_type": res.request_type,
                "created_at": str(res.created_at),
                "updated_at": str(res.updated_at),
            }
            return res_data
        except:
            return "Ticket not found"

    except Exception as e:
        print(e)
        return "Server error"


async def get_filtered_ticket(user_id, filter: str, db: _orm.Session):
    try:
        # Verify user.
        user = await get_user_by_id(user_id, db)
        if user == None:
            return "User not found"
        if user.is_admin:
            try:
                res = (
                    db.query(_models.Ticket)
                    .filter(_models.Ticket.status == filter)
                    .all()
                )
                res_data = {
                    "id": res.id,
                    "text": res.text,
                    "status": res.status,
                    "request_type": res.request_type,
                    "created_at": str(res.created_at),
                    "updated_at": str(res.updated_at),
                }
                return res_data
            except Exception as e:
                print(e)
                return "Ticket not found"
        return "You are not admin"
    except Exception as e:
        print(e)
        return "Server error"


async def get_ticket_history(user_id, db: _orm.Session):
    try:
        # Verify user.
        user = await get_user_by_id(user_id, db)
        if user == None:
            return "User not found"

        if user.is_admin:
            try:
                return db.query(_models.Ticket_history).all()
            except Exception as e:
                print(e)
                return "Ticket not found"
        return "You are not admin"
    except Exception as e:
        print(e)
        return "Server error"


async def get_tickets(user_id, db: _orm.Session):
    try:
        # Verify user.
        user = await get_user_by_id(user_id, db)
        if user == None:
            return "User not found"

        if user.is_admin:
            res = db.query(_models.Ticket).all()

            res_data = []
            for item in res:
                result = {
                    "id": item.id,
                    "text": item.text,
                    "status": item.status,
                    "request_type": item.request_type,
                    "created_at": str(item.created_at),
                    "updated_at": str(item.updated_at),
                }
                res_data.append(result)
            return res_data

        try:
            res = (
                db.query(_models.Ticket)
                .filter(_models.Ticket.user_id == str(user_id))
                .all()
            )
            res_data = []
            for item in res:
                result = {
                    "id": item.id,
                    "text": item.text,
                    "status": item.status,
                    "request_type": item.request_type,
                    "created_at": str(item.created_at),
                    "updated_at": str(item.updated_at),
                }
                res_data.append(result)
            return res_data
        except:
            return "Ticket not found"

    except Exception as e:
        print(e)
        return "Server error"


async def remove_ticket(user_id, ticket_id: int, db: _orm.Session):
    try:
        # Verify user.
        user = await get_user_by_id(user_id, db)
        if user == None:
            return "User not found"

        try:
            model = (
                db.query(_models.Ticket).filter(_models.Ticket.id == ticket_id).first()
            )

            """
            Check if the user already removed the ticket, 
            then don't allow to remove it once again.
            """
            if model.status == TicketEnum.CANCELLED:
                return "Already removed"

            model.status = TicketEnum.CANCELLED
            db.commit()
            res = "success"
        except:
            res = "Ticket not found"
        return res
    except Exception as e:
        print(e)
        return "Server error"


async def resolve_ticket_by_admin(user_id, ticket_id: int, db: _orm.Session):
    try:
        # Verify user.
        user = await get_user_by_id(user_id, db)
        if user == None:
            return "User not found"

        # Verify user is admin.
        if user.is_admin:
            try:
                model = (
                    db.query(_models.Ticket)
                    .filter(_models.Ticket.id == ticket_id)
                    .first()
                )

                """
                Check if the user removed the ticket or it's already resolved, 
                then don't allow the admin to resolve it.
                """
                if model.status == TicketEnum.CANCELLED:
                    return "Already removed"
                if model.status == TicketEnum.RESOLVED:
                    return "Already resolved"

                model.status = TicketEnum.RESOLVED
                db.commit()
                res = "success"
            except:
                res = "Ticket not found"
        else:
            res = "User is not the admin"

        return res
    except Exception as e:
        print(e)
        return "Server error"
