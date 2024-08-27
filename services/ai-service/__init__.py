import uvicorn

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/send-message")
def send_message():
    return {"response": "Hello World!"}
    
    


def run():
    uvicorn.run(app,host="0.0.0.0", port=8080)


if __name__ == "__main__":
    run()    