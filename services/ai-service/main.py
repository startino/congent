import asyncio
from time import sleep
from uuid import UUID
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import graphrag_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def redirect_to_docts():
    return RedirectResponse(url="/docs")


# Should this be in a model folder?
class ChatRequest(BaseModel):
    session_id: UUID
    user_message: str


async def fake_video_streamer():
    for i in range(10):
        sleep(1)
        yield b"some fake video bytes"


@app.post("/chat")
async def send_message(chat_request: ChatRequest):
    value = graphrag_agent.ainvoke_graphrag_agent(chat_request.session_id, chat_request.user_message)

    return StreamingResponse(fake_video_streamer())
    
    
