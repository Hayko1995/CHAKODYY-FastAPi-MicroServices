from abc import ABC
import json
from fastapi import Depends
import websocket
import db.models as _models
import db.database as _database
from ast import literal_eval
import sqlalchemy.orm as _orm

from depends import get_redis_service
from routing.converter import convert_Immediately
from services.convert import RedisService

import sqlalchemy as db


class Transaction(ABC):

    def __init__(self) -> None:
        self.redis = get_redis_service()
        self.engine = db.create_engine(_database.DATABASE_URL)
        self.connection = self.engine.connect()

    def on_message(self, ws, message):
        global current_price
        data = json.loads(message)
        current_price = float(data["p"])

        # print(f"Current price: {current_price}")
        transaction = self.redis.get_value(current_price)
        if not transaction is None:

            data = literal_eval(transaction.decode("utf8"))
            transaction = json.dumps(data, indent=4, sort_keys=True)
            data["price_coin"] = current_price

            return convert_Immediately(data)

    def on_error(self, ws, error):
        # print(f"Error: {error}")
        pass

    def on_close(self, ws):
        print("WebSocket closed")

    def on_open(self, ws):
        symbol = "btcusdt"
        ws.send(
            json.dumps(
                {"method": "SUBSCRIBE", "params": [f"{symbol}@aggTrade"], "id": 1}
            )
        )

    def run_websocket(self):

        self.ws = websocket.WebSocketApp(
            "wss://stream.binance.com:443/ws",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.on_open = self.on_open
        self.ws.run_forever()
