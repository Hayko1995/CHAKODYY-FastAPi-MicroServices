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


class Coin(_database.Base):
    __tablename__ = "coin"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    user_id = relationship("Profile", back_populates="user", uselist=False)
    coin_name = relationship("Profile", back_populates="convert", uselist=False)
    coin_id = _sql.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)



class Convert(_database.Base):
    __tablename__ = "convert"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    coin_from = relationship("Coin", back_populates="user", uselist=False)
    coin_to = relationship("Coin", back_populates="convert", uselist=False)
    count = _sql.Column(_sql.Integer)
