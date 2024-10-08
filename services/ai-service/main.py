import asyncio
import json
from time import sleep
from uuid import UUID
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse

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

@app.post("/chat")
async def send_message(chat_request: ChatRequest):
    value = graphrag_agent.ainvoke_graphrag_agent(chat_request.session_id, chat_request.user_message)

    return EventSourceResponse(value, media_type="text/event-stream")
    
    
