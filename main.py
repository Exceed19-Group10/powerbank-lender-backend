from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import powerbank


app = FastAPI()
app.include_router(powerbank.router)


origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"msg" : "Welcome to root page"}