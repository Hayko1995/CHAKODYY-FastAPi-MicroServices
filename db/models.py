from dataclasses import dataclass
import datetime as _dt
import enum
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from passlib.hash import pbkdf2_sha256
from apps.contest.schemas import StatusEnum
from sqlalchemy import Date
from db.database import Base, engine
import db.database as database
from sqlalchemy import Enum
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import pytz

from passlib.hash import pbkdf2_sha256
from sqlalchemy.sql import func

Base.metadata.create_all(engine)

local_tz = pytz.timezone("Asia/Dubai")


def get_local_time():
    return _dt.datetime.now(local_tz)


class User(database.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True)
    name = _sql.Column(_sql.String)
    username = _sql.Column(_sql.String)
    email = _sql.Column(_sql.String, unique=True, index=True)
    is_verified = _sql.Column(_sql.Boolean, default=False)
    is_admin = _sql.Column(_sql.Boolean, default=False)
    otp = _sql.Column(_sql.Integer)
    otp_created_at = _sql.Column(_sql.DateTime, default=get_local_time())
    hashed_password = _sql.Column(_sql.String)
    address = _sql.Column(_sql.String, default="")
    street = _sql.Column(_sql.String, default="")
    state = _sql.Column(_sql.String, default="")
    city = _sql.Column(_sql.String, default="")
    country = _sql.Column(_sql.String, default="")
    pincode = _sql.Column(_sql.String, default="")
    nationality = _sql.Column(_sql.String, default="")
    preference_timezone = _sql.Column(_sql.String, default="")
    preference_language = _sql.Column(_sql.String, default="")
    preference_login_method = _sql.Column(_sql.String, default="")
    created_at = _sql.Column(_sql.DateTime, default=get_local_time())
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
    name = _sql.Column(_sql.String, nullable=False, unique=False)
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
    ticket_number = _sql.Column(_sql.String, unique=True)
    user_id = _sql.Column(_sql.String, unique=False)
    action_owner = _sql.Column(_sql.Integer, unique=False, default=0)
    text = _sql.Column(_sql.String, unique=False)
    reporting_app = _sql.Column(_sql.String, unique=False, default="something")
    status = _sql.Column(_sql.String, unique=False)
    subject = _sql.Column(_sql.String, unique=False)
    request_type = _sql.Column(_sql.String, unique=False)
    created_at = _sql.Column(_sql.DateTime, default=get_local_time())
    updated_at = _sql.Column(
        _sql.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )


class Ticket_history(database.Base):
    __tablename__ = "ticket_history"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True)
    ticket_number = _sql.Column(_sql.String, unique=False)
    ticket_message = _sql.Column(_sql.String, unique=False)
    created_by = _sql.Column(_sql.Integer, unique=False, default=0)
    created_at = _sql.Column(_sql.DateTime, default=get_local_time())


class Contest(database.Base):
    __tablename__ = "contest"

    contest_id = _sql.Column(
        _sql.Integer, primary_key=True, index=True, autoincrement=True
    )
    title = _sql.Column(_sql.String, unique=False)
    category = _sql.Column(_sql.String, unique=False)
    start_time = _sql.Column(Date)
    end_time = _sql.Column(Date)
    reward = _sql.Column(_sql.String, default="USDT")
    status = _sql.Column(_sql.String, default=StatusEnum.upcoming)
    contest_coins = _sql.Column(_sql.String, unique=False)
    trading_balance = _sql.Column(_sql.String, unique=False)
    created_by = _sql.Column(_sql.Integer)
    updated_by = _sql.Column(_sql.Integer)
    created_at = _sql.Column(_sql.DateTime, default=get_local_time())
    updated_at = _sql.Column(
        _sql.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )


class ContestParticipant(database.Base):
    __tablename__ = "contest_participant"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True)
    contest_id = _sql.Column(_sql.Integer)
    participant = _sql.Column(_sql.Integer)

    is_withdrawn = _sql.Column(_sql.Boolean, default=False)
    joining_time = _sql.Column(_sql.DateTime, default=get_local_time())
    withdraw_time = _sql.Column(_sql.DateTime, default=get_local_time())


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
    from_coin = _sql.Column(_sql.String, nullable=False)
    to_coin = _sql.Column(_sql.String, nullable=False)
    order_quantity = _sql.Column(_sql.Float, nullable=False)
    order_status = _sql.Column(_sql.Boolean, nullable=False)
    created_at = _sql.Column(_sql.DateTime, default=get_local_time())
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
    from_coin = _sql.Column(_sql.String, nullable=False)
    to_coin = _sql.Column(_sql.String, nullable=False)
    order_quantity = _sql.Column(_sql.Float, nullable=False)
    order_status = _sql.Column(_sql.Boolean, nullable=False)
    price = _sql.Column(_sql.Float, nullable=False, default=0)
    created_at = _sql.Column(_sql.DateTime, default=get_local_time())
    updated_at = _sql.Column(
        _sql.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
    user_id = _sql.Column(_sql.Integer, nullable=False)
    contest_id = _sql.Column(_sql.Integer, nullable=False)

    class Config:
        orm_mode = True


class CoinSet(database.Base):
    __tablename__ = "coinset"

    id = _sql.Column(
        _sql.Integer, primary_key=True, index=True, autoincrement=True
    )
    buy_pair = _sql.Column(_sql.String, nullable=False)
    sell_pair = _sql.Column(_sql.String, nullable=False)
