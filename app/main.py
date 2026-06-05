from fastapi import FastAPI
from app.db.init_db import init_db

from app.api.routes import users, auth, products, orders

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/")
def root():
    return {"message": "OMS running"}
