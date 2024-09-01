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


@app.get("/chat")
def send_message(thread_id: str, user_message: str):
    result, checkpoint = graphrag_agent.invoke(thread_id, user_message)
    
    return {"result": result, "checkpoint": checkpoint}
    
    


def run():
    uvicorn.run(app,host="0.0.0.0", port=8080)


if __name__ == "__main__":
    run()    