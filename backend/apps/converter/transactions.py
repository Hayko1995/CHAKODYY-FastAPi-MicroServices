from abc import ABC
import json
from fastapi import Depends
import websocket
import db.models as _models
import db.database as database
from ast import literal_eval
import sqlalchemy.orm as _orm

from depends import get_redis_service
from apps.converter.router import convert_immediately
from apps.converter.service import RedisService

import asyncio
import websockets
import json

import sqlalchemy as db
import websocket

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Transaction(ABC):

    def __init__(self) -> None:
        self.redis = get_redis_service()
        self.engine = db.create_engine(database.DATABASE_URL)
        self.connection = self.engine.connect()

    def on_message(self, ws, message):
        global current_price
        data = json.loads(message)
        current_price = float(data["p"])

        byte_literals = self.redis.get_keys()
        if byte_literals != []:
            string_values = [x.decode("utf-8") for x in byte_literals]

            # Step 2: Convert to floats
            float_values = [float(x) for x in string_values]

            smaller_values = [value for value in float_values if value < current_price]
            for value in smaller_values:
                transactions = self.redis.get_value(str(value))
                self.redis.delete_value(str(value))
                if transactions is not None:
                    transactions = literal_eval(transactions.decode("utf8"))
                    for transaction in transactions:
                        if "stop_convert" in transaction:
                            transaction["price"] = transaction["stop_convert"]
                            del transaction["stop_convert"]
                            # limit_buy(transaction) # todo add buy or cell
                        else:
                            transaction["price_coin"] = current_price
                            convert_immediately(transaction)

        return {"status": "done"}

    async def binance_ws(self):
        url = "wss://stream.binance.com:9443/ws/!ticker@arr"

        async with websockets.connect(url) as ws:
            while True:
                data = await ws.recv()
                data_json = json.loads(data)

                for ticker in data_json:
                    if ticker["s"] == "BTCUSDT":
                        pass
                        # print(f"BTC/USDT Price: {ticker['c']}")
                    elif ticker["s"] == "ETHUSDT":
                        pass
                        # print(f"ETH/USDT Price: {ticker['c']}")
                    elif ticker["s"] == "SOLUSDT":
                        pass
                        # print(f"SOL/USDT Price: {ticker['c']}")
                    elif ticker["s"] == "NEARUSDT":
                        # print(f"NEAR/USDT Price: {ticker['c']}")
                        pass
                    elif ticker["s"] == "MATICUSDT":
                        # print(f"MATI/CUSDT Price: {ticker['c']}")
                        pass
                    elif ticker["s"] == "TRXUSDT":
                        # print(f"TRX/USDT Price: {ticker['c']}")
                        pass
                    elif ticker["s"] == "PEOPLEUSDT":
                        # print(f"PEOPLE/USDT Price: {ticker['c']}")
                        pass
                    elif ticker["s"] == "IOUSDT":
                        # print(f"IO/USDT Price: {ticker['c']}")
                        pass
                    elif ticker["s"] == "DOGEUSDT":
                        # print(f"DOGE/USDT Price: {ticker['c']}")
                        pass
                    elif ticker["s"] == "BNBUSDT":
                        # print(f"BNB/USDT Price: {ticker['c']}")
                        pass

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.binance_ws())


class WebSocketClient(ABC):
    def __init__(self):
        self.ws = websocket.WebSocketApp(
            "ws://binanacetestserver:5005/ws",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.redis = get_redis_service()
        self.engine = db.create_engine(database.DATABASE_URL)
        self.connection = self.engine.connect()

        self.ws.on_open = self.on_open

    def on_message(self, ws, message):

        global current_price
        data = json.loads(message)
        current_price = float(data["p"])

        byte_literals = self.redis.get_keys()
        if byte_literals != []:
            string_values = [x.decode("utf-8") for x in byte_literals]

            # Step 2: Convert to floats
            float_values = [float(x) for x in string_values]

            smaller_values = [value for value in float_values if value < current_price]
            for value in smaller_values:
                transactions = self.redis.get_value(str(value))
                self.redis.delete_value(str(value))
                if transactions is not None:
                    transactions = literal_eval(transactions.decode("utf8"))
                    for transaction in transactions:
                        if "stop_convert" in transaction:
                            transaction["price"] = transaction["stop_convert"]
                            del transaction["stop_convert"]
                            # limit(transaction)
                        else:
                            transaction["price_coin"] = current_price
                            convert_immediately(transaction)

        return {"status": "done"}

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(self, ws):
        pass
        # def run():
        #     while True:
        #         message = input("Enter a message to send: ")
        #         ws.send(message)
        # run()

    def start(self):
        self.ws.run_forever()
