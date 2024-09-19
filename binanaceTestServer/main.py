# from fastapi import FastAPI, WebSocket
# from fastapi.responses import HTMLResponse
# import json
# app = FastAPI()


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):

#     # await websocket.accept()
#     while True:
#         data = {"e":"aggTrade","E":1726740609682,"s":"BTCUSDT","a":3158570747,"p":"62504.91000000","q":"0.00040000","f":3835586829,"l":3835586832,"T":1726740609681,"m":True,"M":True}
#         data = json.dump(data)
#         await websocket.send_text('data')


# # Start the FastAPI server
# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run("main:app", host="0.0.0.0", port=5005, reload=True)


import json
from fastapi import FastAPI, WebSocket
import uvicorn
import asyncio
import time

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = {
                "e": "aggTrade",
                "E": 1726740609682,
                "s": "BTCUSDT",
                "a": 3158570747,
                "p": "62504.91000000",
                "q": "0.00040000",
                "f": 3835586829,
                "l": 3835586832,
                "T": 1726740609681,
                "m": True,
                "M": True,
            }
            data = json.dumps(data)

            # Send the data to the WebSocket client
            await websocket.send_text(data)

            # Wait for 1 second before sending the next message
            await asyncio.sleep(1)

    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5005)
