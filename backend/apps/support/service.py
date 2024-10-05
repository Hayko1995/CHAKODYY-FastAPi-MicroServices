import db.models as _models
import sqlalchemy.orm as _orm

from apps.auth.service import get_user_by_id
from apps.support.schemas import Ticket, TicketEnum


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


async def remove_ticket(user_id, ticket: int, db: _orm.Session):
    try:
        # Verify user.
        user = await get_user_by_id(user_id, db)
        if user == None:
            return "User not found"
        
        try:
            model = (
                db.query(_models.Ticket).filter(_models.Ticket.id == ticket).first()
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


async def resolve_ticket_by_admin(user_id, ticket: int, db: _orm.Session):
    try:
        # Verify user.
        user = await get_user_by_id(user_id, db)
        if user == None:
            return "User not found"
        
        # Verify user is admin.
        if user.is_admin:
            try:
                model = (
                    db.query(_models.Ticket).filter(_models.Ticket.id == ticket).first()
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