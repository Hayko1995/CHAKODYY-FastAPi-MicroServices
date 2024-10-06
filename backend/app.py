import logging
import threading

from dotenv import load_dotenv
from fastapi import FastAPI


from apps.auth.router import auth
from apps.contest.router import contest
from apps.converter.router import coin
from apps.converter.router import router as converter
from apps.converter.transactions import Transaction
from apps.support.router import support
from db import models as _models

from apps.converter.transactions import Transaction
from apps.converter.router import router as converter
from apps.auth.router import auth
from apps.support.router import support
from apps.contest.router import contest
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(openapi_url="/core/openapi.json", docs_url="/docs")
app.include_router(converter)
app.include_router(auth)
app.include_router(support)
app.include_router(contest)

logging.basicConfig(level=logging.INFO)

_models.Base.metadata.create_all(_models.engine)


@app.on_event("startup")
def start_websocket():
    # Run the WebSocket in a separate thread
    threading.Thread(target=Transaction().run, daemon=True).start()


# # Start the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5003, reload=True)
