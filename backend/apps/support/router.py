import apps.support.service as services
import db.database as database
import fastapi
import sqlalchemy.orm as orm

from apps.auth.router import jwt_validation
from apps.support import schemas

from fastapi import Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

support = fastapi.APIRouter(prefix="/support", tags=["support"])
oauth2schema = OAuth2PasswordBearer(tokenUrl="/auth/token")


@support.post("/ticket")
async def create_ticket(
    ticket: schemas.CreateTicketRequest,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    ticket_obj = await services.create_ticket(
        user_id=payload["id"], ticket=ticket, db=db
    )
    if ticket_obj:
        data = {"message": "The ticket is created"}
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)
    else:
        data = {"message": "Internal Server Error"}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=data
        )


@support.put("/ticket")
async def update_ticket(
    ticket: schemas.UpdateTicketRequest,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    res = await services.update_ticket(user_id=payload["id"], ticket=ticket, db=db)
    if res == "success":
        data = {"message": "The ticket is updated successfully"}
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)
    if res == "User not found":
        data = {"message": "User not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Ticket not found":
        data = {"message": "Ticket not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    else:
        data = {"message": "Internal Server Error"}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=data
        )


@support.get("/ticket")
async def get_ticket(
    ticket_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    res = await services.get_ticket(user_id=payload["id"], ticket_id=ticket_id, db=db)
    if res == "User not found":
        data = {"message": "User not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Ticket not found":
        data = {"message": "Ticket not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Server error":
        data = {"message": "Internal Server Error"}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=data
        )
    else:
        return JSONResponse(status_code=status.HTTP_200_OK, content=res)


@support.get("/filtered_ticket")
async def get_filtered_ticket(
    filter: str,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    res = await services.get_filtered_ticket(
        user_id=payload["id"], filter=filter, db=db
    )
    if res == "User not found":
        data = {"message": "User not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Ticket not found":
        data = {"message": "Ticket not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Server error":
        data = {"message": "Internal Server Error"}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=data
        )
    else:
        return JSONResponse(status_code=status.HTTP_200_OK, content=res)


@support.get("/ticket_history")
async def get_ticket_history(
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    res = await services.get_ticket_history(user_id=payload["id"], db=db)
    if res == "User not found":
        data = {"message": "User not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Ticket not found":
        data = {"message": "Ticket not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Server error":
        data = {"message": "Internal Server Error"}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=data
        )
    else:
        return res


@support.get("/tickets")
async def get_tickets(
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    res = await services.get_tickets(user_id=payload["id"], db=db)
    if res == "User not found":
        data = {"message": "User not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Ticket not found":
        data = {"message": "Ticket not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Server error":
        data = {"message": "Internal Server Error"}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=data
        )
    else:
        return JSONResponse(status_code=status.HTTP_200_OK, content=res)


@support.delete("/ticket")
async def remove_ticket(
    ticket_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):

    res = await services.remove_ticket(
        user_id=payload["id"], ticket_id=ticket_id, db=db
    )
    if res == "success":
        data = {"message": "Ticket deleted successfully"}
        return JSONResponse(status_code=status.HTTP_200_OK, content=data)
    if res == "Already removed":
        data = {"message": "The ticket is already removed"}
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)
    if res == "User not found":
        data = {"message": "User not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Ticket not found":
        data = {"message": "Ticket not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Server error":
        data = {"message": "Internal Server Error"}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=data
        )


@support.post("/resolve-ticket")
async def resolve_ticket_by_admin(
    ticket_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    res = await services.resolve_ticket_by_admin(
        user_id=payload["id"], ticket_id=ticket_id, db=db
    )
    if res == "success":
        data = {"message": "Ticket resolved successfully"}
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)
    if res == "Already removed":
        data = {"message": "The ticket is already removed"}
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)
    if res == "Already resolved":
        data = {"message": "The ticket is already resolved"}
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)
    if res == "User not found":
        data = {"message": "User not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Ticket not found":
        data = {"message": "Ticket not found"}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)
    if res == "Server error":
        data = {"message": "Internal Server Error"}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=data
        )
