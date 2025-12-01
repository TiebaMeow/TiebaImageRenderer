from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from ..config import config

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def start_server():
    uvicorn.run(app, host=config.host, port=config.port)
