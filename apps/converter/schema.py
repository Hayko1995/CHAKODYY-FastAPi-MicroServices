import uuid

from datetime import datetime
from pydantic import BaseModel


class Author(BaseModel):
    first_name: str
    last_name: str
    date_birth: datetime
    biography: str


class Book(BaseModel):
    title: str
    annotation: str
    date_publishing: datetime
    author: Author


class Market(BaseModel):
    buy: bool = True
    coin1: str
    coin2: str
    price: float
    count: float
    
class DeletePanding(BaseModel):
    coin_set: str
    row: dict


class CoinSet(BaseModel):
    coin1: str
    coin2: str

class UpdateCoinSet(BaseModel):
    id: int
    coin1: str
    coin2: str

class ConvertRequest(BaseModel):
    from_coin: str
    to_coin: str
    count_coin: str
    price_coin: str


class BuyCoin(BaseModel):
    coin_uuid: uuid.uuid4
    coin_name: str
    coin_count: float


class BuyRequest(BaseModel):
    coin_name: str
    coin_count: float


class CoinScema(BaseModel):
    uuid: str
    name: str
    count: float
    user_id: int


class ReqBody(BaseModel):
    coin_name: str
    coin_count: float
