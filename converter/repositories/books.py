from typing import List


from db import models
from schemas.schema import Book


class BookRepository:

    def get_books(self) -> List[Book]:
        raise NotImplemented

    def create_book(self) -> Book:
        raise NotImplemented


class ConvertRepository:

    def convert_coin(self) -> List[Book]:
        raise NotImplemented

    def buy_coin(self) -> dict:
        raise NotImplemented

    def get_coin(self, id, coin, db) -> models.CoinAccount:
        try:
            coin = (
                db.query(models.CoinAccount)
                .filter(
                    models.CoinAccount.user_id == id,
                    models.CoinAccount.name == coin,
                )
                .first()
            )
            return coin
        except Exception as e:
            raise NotImplemented


class RedisRepository:

    def get_value(self, key) -> List[dict]:
        raise NotImplemented

    def get_keys(self, key) -> List[dict]:
        raise NotImplemented

    def set_value(self) -> None:
        raise NotImplemented
