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
    ticket: schemas.Ticket,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    ticket_obj = await services.create_ticket(user_id=payload["id"], ticket=ticket, db=db)
    if ticket_obj:
        data = {"message": "The ticket is created"}
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)
    else:
        data = {"message": "Internal Server Error"}
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=data)


@support.get("/ticket")
async def get_ticket(
    ticket: int = -1,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):

    return await services.get_tickets(user_id=payload["id"], ticket=ticket, db=db)


@support.delete("/ticket")
async def remove_ticket(
    ticket: int = -1,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):

    res = await services.remove_ticket(user_id=payload["id"], ticket=ticket, db=db)
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
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=data)
    

@support.post("/resolve-ticket")
async def resolve_ticket_by_admin(
    ticket: int = -1,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    res = await services.resolve_ticket_by_admin(user_id=payload["id"], ticket=ticket, db=db)
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
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=data)
