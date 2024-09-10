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
    

class ConvertRequest(BaseModel):
    from_coin: str
    to_coin: str
    count_coin: str
    price_coin: str

class BuyRequest(BaseModel):
    coin_name: str
    coin_count: float