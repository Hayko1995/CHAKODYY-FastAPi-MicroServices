from abc import ABC
import json
from fastapi import Depends
import websocket
from apps.converter.router import market_buy_coin, market_sell_coin
from apps.converter.schema import Market
import db.models as _models
import db.database as database
from ast import literal_eval
import sqlalchemy.orm as _orm

import asyncio
import websockets
import json

import websocket

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Transaction(ABC):

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
                            # convert_immediately(transaction)

        return {"status": "done"}

    def get_rows_from_db(self, row_coin_set: str):
        db = database.SessionLocal()
        coin_sets = (
            db.query(_models.OrderPending)
            .filter(_models.OrderPending.order_coin == row_coin_set)
            .all()
        )
        return coin_sets

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
        pass
        # rows = self.get_rows_from_db(coin)
        # for row in rows:
        #     if row.order_direction == "buy":
        #         if float(row.price) < float(ticker["c"]):
        #             self.delete_row(order_id=row.order_id)
        #             market = Market(
        #                 coin_set=row.order_coin,
        #                 price=row.price,
        #                 count=row.order_quantity,
        #             )
        #             market_buy_coin(market)
        #     else:
        #         if float(row.price) > float(ticker["c"]):
        #             self.delete_row(order_id=row.order_id)
        #             market = Market(
        #                 coin_set=row.order_coin,
        #                 price=row.price,
        #                 count=row.order_quantity,
        #             )
        #             market_sell_coin(market)

    async def binance_ws(self):
        url = "wss://stream.binance.com:9443/ws/!ticker@arr"

        async with websockets.connect(url) as ws:
            while True:
                await asyncio.sleep(1)
                data = await ws.recv()
                data_json = json.loads(data)
                for ticker in data_json:
                    if ticker["s"] == "BTCUSDT":
                        self.process("BTC/USDT", ticker)
                    elif ticker["s"] == "ETHUSDT":
                        self.process("ETH/USDT", ticker)
                    elif ticker["s"] == "SOLUSDT":
                        self.process("SOL/USDT", ticker)
                    elif ticker["s"] == "NEARUSDT":
                        self.process("NEAR/USDT", ticker)
                    elif ticker["s"] == "MATICUSDT":
                        self.process("MATIC/USDT", ticker)
                    elif ticker["s"] == "TRXUSDT":
                        self.process("TRX/USDT", ticker)
                    elif ticker["s"] == "PEOPLEUSDT":
                        self.process("PEOPLE/USDT", ticker)
                    elif ticker["s"] == "IOUSDT":
                        self.process("IOU/USDT", ticker)
                    elif ticker["s"] == "DOGEUSDT":
                        self.process("DOGE/USDT", ticker)
                    elif ticker["s"] == "BNBUSDT":
                        self.process("BNB/USDT", ticker)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.binance_ws())
