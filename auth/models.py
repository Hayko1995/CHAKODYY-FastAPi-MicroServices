import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import database as _database

from database import Base, engine
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
    otp = _sql.Column(_sql.Integer)
    otp_created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    hashed_password = _sql.Column(_sql.String)
    created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    updated_at = _sql.Column(_sql.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

    def verify_password(self, password: str):
        return pbkdf2_sha256.verify(password, self.hashed_password)
