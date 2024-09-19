from abc import ABC
import json
from fastapi import Depends
import websocket
import db.models as _models
import db.database as _database
from ast import literal_eval
import sqlalchemy.orm as _orm

from depends import get_redis_service
from apps.converter.routing.converter import convert_Immediately, limit
from apps.converter.services.convert import RedisService

import sqlalchemy as db


class Transaction(ABC):

    def __init__(self) -> None:
        self.redis = get_redis_service()
        self.engine = db.create_engine(_database.DATABASE_URL)
        self.connection = self.engine.connect()

    def on_message(self, ws, message):
        global current_price
        tolerance = 0.5
        data = json.loads(message)
        current_price = float(data["p"])

        byte_literals = self.redis.get_keys()
        if not byte_literals == []:
            string_values = [x.decode("utf-8") for x in byte_literals]

            # Step 2: Convert to floats
            float_values = [float(x) for x in string_values]

            smaller_values = [value for value in float_values if value < current_price]
            for value in smaller_values:
                transactions = self.redis.get_value(str(value))
                self.redis.delete_value(str(value))
                if not transactions is None:
                    transactions = literal_eval(transactions.decode("utf8"))
                    for transaction in transactions:
                        # transaction = json.dumps(data, indent=4, sort_keys=True)
                        if "stop_convert" in transaction:
                            transaction["price"] = transaction["stop_convert"]
                            del transaction["stop_convert"]
                            limit(transaction)
                        else:
                            transaction["price_coin"] = current_price
                            convert_Immediately(transaction)

        return {"status": "done"}

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
