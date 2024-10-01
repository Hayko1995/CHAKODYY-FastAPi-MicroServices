from dataclasses import dataclass
import datetime as _dt
import enum
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from passlib.hash import pbkdf2_sha256
from db.database import Base, engine
import db.database as database
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


class User(database.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True)
    name = _sql.Column(_sql.String)
    username = _sql.Column(_sql.String)
    email = _sql.Column(_sql.String, unique=True, index=True)
    is_verified = _sql.Column(_sql.Boolean, default=False)
    is_admin = _sql.Column(_sql.Boolean, default=False)
    otp = _sql.Column(_sql.Integer)
    otp_created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.now)
    hashed_password = _sql.Column(_sql.String)
    created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.now)
    updated_at = _sql.Column(
        _sql.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    def verify_password(self, password: str):
        return pbkdf2_sha256.verify(password, self.hashed_password)


class BuyHistory(database.Base):
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


class Balance(database.Base):
    __tablename__ = "balance"

    uuid = _sql.Column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True
    )
    name = _sql.Column(_sql.String, nullable=False, unique=True)
    count = _sql.Column(_sql.Float, nullable=False)
    user_id = _sql.Column(_sql.Integer, nullable=False)

    class Config:
        orm_mode = True


class Convert(database.Base):
    __tablename__ = "convert"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True)
    coin_from = _sql.Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=False, nullable=False
    )
    coin_to = _sql.Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=False, nullable=False
    )
    count = _sql.Column(_sql.Integer)


class Ticket(database.Base):
    __tablename__ = "ticket"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True)
    user_id = _sql.Column(_sql.String, unique=False)
    text = _sql.Column(_sql.String, unique=False)
    status = _sql.Column(_sql.String, unique=False)
    request_type = _sql.Column(_sql.String, unique=False)
    created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.now)
    updated_at = _sql.Column(
        _sql.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )


class Contest(database.Base):
    __tablename__ = "contest"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True)
    title = _sql.Column(_sql.String, unique=True)
    category = _sql.Column(_sql.String, unique=False)
    start_time = _sql.Column(_sql.DateTime)
    end_time = _sql.Column(_sql.DateTime)
    reward = _sql.Column(_sql.String, unique=False)
    contest_coins = _sql.Column(_sql.String, unique=False)
    trading_balance = _sql.Column(_sql.String, unique=False)
    created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.now)
    updated_at = _sql.Column(
        _sql.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )


class ContestParticipant(database.Base):
    __tablename__ = "contest_participant"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True)
    contest_id = _sql.Column(_sql.Integer)
    participant = _sql.Column(_sql.Integer)

    is_withdrawn = _sql.Column(_sql.Boolean, default=False)
    joining_time = _sql.Column(_sql.DateTime, default=_dt.datetime.now)
    withdraw_time = _sql.Column(_sql.DateTime, default=_dt.datetime.now)


class CoinSet(database.Base):
    __tablename__ = "coin_set"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True)
    coins = _sql.Column(_sql.String, unique=True)
    created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.now)
    updated_at = _sql.Column(
        _sql.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )


class Status(enum.Enum):
    DRAFT = "draft"
    APPROVE = "approve"
    PUBLISHED = "published"


class OrderArchived(database.Base):
    __tablename__ = "order_archived"

    order_id = _sql.Column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True
    )
    order_type = _sql.Column(_sql.String, nullable=False)
    order_direction = _sql.Column(_sql.String, nullable=False)
    order_coin = _sql.Column(_sql.String, nullable=False)
    order_quantity = _sql.Column(_sql.Float, nullable=False)
    order_status = _sql.Column(_sql.Boolean, nullable=False)
    created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.now)
    price = _sql.Column(_sql.Float, nullable=False, default=0)
    updated_at = _sql.Column(
        _sql.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
    user_id = _sql.Column(_sql.Integer, nullable=False)
    contest_id = _sql.Column(_sql.Integer, nullable=False)

    class Config:
        orm_mode = True


class OrderPending(database.Base):
    __tablename__ = "order_pending"

    order_id = _sql.Column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True
    )
    order_type = _sql.Column(_sql.String, nullable=False)
    order_direction = _sql.Column(_sql.String, nullable=False)
    order_coin = _sql.Column(_sql.String, nullable=False)
    order_quantity = _sql.Column(_sql.Float, nullable=False)
    order_status = _sql.Column(_sql.Boolean, nullable=False)
    price = _sql.Column(_sql.Float, nullable=False, default=0)
    created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.now)
    updated_at = _sql.Column(
        _sql.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
    user_id = _sql.Column(_sql.Integer, nullable=False)
    contest_id = _sql.Column(_sql.Integer, nullable=False)

    class Config:
        orm_mode = True
