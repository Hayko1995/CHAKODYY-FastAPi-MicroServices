import logging
import os
from typing import Any
from fastapi import Depends, HTTPException
import pika

import fastapi
from fastapi import BackgroundTasks
import uvicorn
import sqlalchemy.orm as orm


from apps.contest import schemas
import apps.contest.service as services

from datetime import datetime


from apps.auth.router import jwt_validation
import db.database as database


contest = fastapi.APIRouter(prefix="/contest", tags=["contest"])


@contest.post("/contest")
async def create_contest(
    contest: schemas.CreateContest,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    status = await services.create_contest(contest=contest, db=db)
    if status:
        return fastapi.HTTPException(
            status_code=201,
            detail="Created",
        )
    else:
        return fastapi.HTTPException(
            status_code=500,
            detail="Server side error",
        )


@contest.get("/contest")
async def get_contest(
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    try:
        return await services.get_contest(db=db)
    except Exception as e:
        print(e)
        return fastapi.HTTPException(
            status_code=500,
            detail="Server side error",
        )


@contest.delete("/contest")
async def delete_contest(
    id: str,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    status = await services.delete_contest(payload=payload, id=id, db=db)
    if status:
        return fastapi.HTTPException(
            status_code=200,
            detail="Deleted",
        )
    else:
        return fastapi.HTTPException(
            status_code=500,
            detail="Server side error",
        )


@contest.post("/join")
async def get_contest(
    ticket: int = -1,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):

    return await services.get_tickets(user_id=payload["id"], ticket=ticket, db=db)


@contest.post("/exit")
async def exit_contest(
    ticket: int = -1,
    db: orm.Session = fastapi.Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):

    return await services.remove_tickets(user_id=payload["id"], ticket=ticket, db=db)
