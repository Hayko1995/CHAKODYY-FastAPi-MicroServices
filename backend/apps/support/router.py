import logging
import os
from typing import Any
from fastapi import Depends, HTTPException
import pika
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import fastapi
from fastapi import BackgroundTasks
import uvicorn
import sqlalchemy.orm as orm


from apps.support import schemas
import apps.support.service as services

from datetime import datetime


from apps.converter.routing.converter import jwt_validation
from db import models


support = fastapi.APIRouter(prefix="/support", tags=["support"])
oauth2schema = OAuth2PasswordBearer(tokenUrl="/auth/token")


@support.post("/ticket")
async def create_ticket(
    ticket: schemas.Ticket,
    db: orm.Session = fastapi.Depends(services.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    status = await services.create_ticket(user_id=payload["id"], ticket=ticket, db=db)
    if status:
        return fastapi.HTTPException(
            status_code=201,
            detail="Ticket Created",
        )
    else:
        return fastapi.HTTPException(
            status_code=500,
            detail="Server side error",
        )


@support.get("/ticket")
async def get_ticket(
    ticket: int = -1,
    db: orm.Session = fastapi.Depends(services.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):

    return await services.get_tickets(user_id=payload["id"], ticket=ticket, db=db)


@support.delete("/ticket")
async def delete_ticket(
    ticket: int = -1,
    db: orm.Session = fastapi.Depends(services.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):

    return await services.remove_tickets(user_id=payload["id"], ticket=ticket, db=db)
