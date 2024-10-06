from typing import List


from db import models


class ConvertRepository:

    def convert_coin(self):
        raise NotImplemented

    def buy_coin(self) -> dict:
        raise NotImplemented

    def get_coin(self, id, coin, db) -> models.Balance:
        try:
            coin = (
                db.query(models.Balance)
                .filter(
                    models.Balance.user_id == id,
                    models.Balance.name == coin,
                )
                .first()
            )
            return coin
        except Exception as e:
            print(e)
            raise NotImplemented


class RedisRepository:

    def get_value(self, key) -> List[dict]:
        raise NotImplemented

    def get_keys(self, key) -> List[dict]:
        raise NotImplemented

    def set_value(self) -> None:
        raise NotImplemented
