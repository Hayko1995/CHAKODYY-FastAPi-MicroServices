from dataclasses import dataclass
import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from passlib.hash import pbkdf2_sha256
from db.database import Base, engine
import db.database as _database
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

Base.metadata.create_all(engine)


@dataclass
class BuyHistory(_database.Base):
    __tablename__ = "buy_history"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True)
    name = _sql.Column(_sql.String, nullable=False)
    count = _sql.Column(_sql.Float, nullable=False)
    user_id = _sql.Column(_sql.Integer, nullable=False)

    class Config:
        orm_mode = True


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
