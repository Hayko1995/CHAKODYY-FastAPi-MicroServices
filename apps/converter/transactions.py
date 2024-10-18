import asyncio
import json
import os
import websocket
import websockets

from depends import get_convert_service, get_redis_service
import db.database as database
import db.models as _models
import sqlalchemy.orm as _orm

from abc import ABC
from ast import literal_eval
from dotenv import load_dotenv
from fastapi import Depends

from apps.converter.schema import Market

# Load environment variables from .env file
load_dotenv()


class Transaction(ABC):

    def get_rows_from_redis(self, coin_set: str):
        redis = get_redis_service()
        rows = redis.get_value(coin_set)
        return rows

    def delete_rows_from_redis(self, key, row):
        redis = get_redis_service()
        status = redis.delete_value(key, row)
        return status

    def delete_row(self, order_id: str):
        db = database.SessionLocal()
        coin_sets = (
            db.query(_models.OrderPending)
            .filter(_models.OrderPending.order_id == order_id)
            .delete()
        )
        db.commit()
        return coin_sets

    def process(self, coin, ticker):
        service = get_convert_service()
        rows = self.get_rows_from_redis(coin)
        if rows:
            for row in json.loads(rows):
                if row["order_direction"] == "buy":
                    if float(row["price"]) < float(ticker["c"]):

                        self.delete_rows_from_redis(coin, row)
                        market = Market(
                            buy=True,
                            coin1=row["from_coin"],
                            coin2=row["to_coin"],
                            price=row["price"],
                            count=row["order_quantity"],
                        )
                        res = service.market(
                            market, id=row["user_id"], db=database.SessionLocal()
                        )

                        print(res)
                else:
                    if float(row["price"]) > float(ticker["c"]):
                        self.delete_row(order_id=row.order_id)
                        market = Market(
                            buy=False,
                            coin1=row["from_coin"],
                            coin2=row["to_coin"],
                            price=row["price"],
                            count=row["order_quantity"],
                        )
                        res = service.market(market, id=id, db=database.SessionLocal())
                        print(res)

    async def binance_ws(self):
        url = "wss://stream.binance.com:9443/ws/!ticker@arr"

        async with websockets.connect(url) as ws:
            while True:
                await asyncio.sleep(1)
                data = await ws.recv()
                data_json = json.loads(data)
                for ticker in data_json:
                    self.process(ticker["s"], ticker)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.binance_ws())
