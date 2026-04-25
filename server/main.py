# api
from fastapi import FastAPI
import subprocess


from server.src.routes.user import user_router
from server.src.core.db.database import engine
from server.src.core.db.database import Base

version = "v1"
app = FastAPI(
    version=version,
    description="An instagram model",
    title="Instagram",
    contact={"contact" : "shreyajagtap758@gmail.com"}
)


from server.src import models

app.include_router(user_router, prefix="/user")
