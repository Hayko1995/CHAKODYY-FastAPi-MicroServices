from typing import List

from schemas.books import Book


class BookRepository:

    def get_books(self) -> List[Book]:
        raise NotImplemented

    def create_book(self) -> Book:
        raise NotImplemented


class RedisRepository:

    def get_value(self, key) -> List[dict]:
        raise NotImplemented

    def get_keys(self, key) -> List[dict]:
        raise NotImplemented

    def set_value(self) -> None:
        raise NotImplemented
