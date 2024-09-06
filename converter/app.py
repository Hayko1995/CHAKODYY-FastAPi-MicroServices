import json
import threading
import websocket
from fastapi import FastAPI, BackgroundTasks
from abc import ABC

from services.transactions import Transaction
from routing.books import router as books_routing


app = FastAPI(openapi_url="/core/openapi.json", docs_url="/docs")
app.include_router(books_routing)


@app.on_event("startup")
def start_websocket():
    # Run the WebSocket in a separate thread
    threading.Thread(target=Transaction().run_websocket, daemon=True).start()


# Start the FastAPI server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=5003, reload=True)
