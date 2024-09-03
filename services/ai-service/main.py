from uuid import UUID
from pydantic import BaseModel
import uvicorn

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
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


@app.post("/chat")
def send_message(chat_request: ChatRequest):
    success = graphrag_agent.invoke(chat_request.session_id, chat_request.user_message)
    
    return {"success": success}
    

def run():
    uvicorn.run(app,host="0.0.0.0", port=8080)

if __name__ == "__main__":
    run()    