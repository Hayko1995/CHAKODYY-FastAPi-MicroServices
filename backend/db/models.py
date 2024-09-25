from dataclasses import dataclass
import datetime as _dt
import enum
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from passlib.hash import pbkdf2_sha256
from db.database import Base, engine
import db.database as _database
from sqlalchemy import Enum
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm

from passlib.hash import pbkdf2_sha256
from sqlalchemy.sql import func

Base.metadata.create_all(engine)


class User(_database.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String)
    username = _sql.Column(_sql.String)
    email = _sql.Column(_sql.String, unique=True, index=True)
    is_verified = _sql.Column(_sql.Boolean, default=False)
    is_admin = _sql.Column(_sql.Boolean, default=False)
    otp = _sql.Column(_sql.Integer)
    otp_created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    hashed_password = _sql.Column(_sql.String)
    created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    updated_at = _sql.Column(
        _sql.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    def verify_password(self, password: str):
        return pbkdf2_sha256.verify(password, self.hashed_password)


class BuyHistory(_database.Base):
    __tablename__ = "buy_history"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True)
    name = _sql.Column(_sql.String, nullable=False)
    count = _sql.Column(_sql.Float, nullable=False)
    user_id = _sql.Column(_sql.Integer, nullable=False)

    class Config:
        orm_mode = True


class Status(enum.Enum):
    DRAFT = "draft"
    APPROVE = "approve"
    PUBLISHED = "published"


class CoinAccount(_database.Base):
    __tablename__ = "coin_account"

    # id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    uuid = _sql.Column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True
    )
    name = _sql.Column(_sql.String, nullable=False)
    count = _sql.Column(_sql.Float, nullable=False)
    user_id = _sql.Column(_sql.Integer, nullable=False)

    class Config:
        orm_mode = True


class Convert(_database.Base):
    __tablename__ = "convert"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    coin_from = _sql.Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=False, nullable=False
    )
    coin_to = _sql.Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=False, nullable=False
    )
    count = _sql.Column(_sql.Integer)


class Status(enum.Enum):
    ACTIVE = "active"
    ERROR = "error"
    WARNING = "warning"
    ISSUE = "ISSUE"


class Ticket(_database.Base):
    __tablename__ = "ticket"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    user_id = _sql.Column(_sql.String)
    text = _sql.Column(_sql.String, unique=True, index=True)
    status = _sql.Column(
        _sql.Enum(Status, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=Status.ACTIVE.value,
        server_default=Status.ACTIVE.value,
    )