from typing import List

from fastapi.responses import JSONResponse


from db import models
from fastapi import status


class ConvertRepository:

    def convert_coin(self):
        raise NotImplemented

    def buy_coin(self) -> dict:
        raise NotImplemented

    def get_coin(self, id, coin, db) -> models.Balance:
        try:
            coin_row = (
                db.query(models.Balance)
                .filter(
                    models.Balance.user_id == id,
                    models.Balance.name == coin,
                )
                .first()
            )
            if not coin_row:
                if coin == "USDT":
                    coin_row = models.Balance(
                        name="USDT",
                        count=0,
                        user_id=id,
                    )
                    db.add(coin_row)
                    db.commit()
                    db.refresh(coin_row)

            return coin_row
        except Exception as e:
            print(e)
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class RedisRepository:

    def get_value(self, key) -> List[dict]:
        raise NotImplemented

    def get_keys(self, key) -> List[dict]:
        raise NotImplemented

    def set_value(self) -> None:
        raise NotImplemented
