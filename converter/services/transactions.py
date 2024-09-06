
from abc import ABC
import json
import websocket


class Transaction(ABC):

    def on_message(self, ws, message):
        
        global current_price
        data = json.loads(message)
        current_price = float(data["p"])
        # print(f"Current price: {current_price}")


    def on_error(self, ws, error):
        # print(f"Error: {error}")
        pass


    def on_close(self, ws):
        print("WebSocket closed")


    def on_open(self, ws):
        symbol = "btcusdt"
        ws.send(
            json.dumps({"method": "SUBSCRIBE", "params": [f"{symbol}@aggTrade"], "id": 1})
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
