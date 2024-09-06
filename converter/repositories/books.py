from typing import List

from schemas.books import Book


class BookRepository:

    def get_books(self) -> List[Book]:
        raise NotImplemented

    def create_book(self) -> Book:
        raise NotImplemented
