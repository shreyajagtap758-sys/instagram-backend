# api
from fastapi import FastAPI
import subprocess


from server.src.routes.follow import follow_router
from server.src.routes.password import password_router
from server.src.routes.user import user_router
from server.src.core.db.database import engine
from server.src.core.db.database import Base


app = FastAPI(
    description="An instagram model",
    title="Instagram",
    contact={"contact" : "shreyajagtap758@gmail.com"}
)


from server.src import models

from server.src.error_handling.register import setup_error_handlers
setup_error_handlers(app)

app.include_router(user_router)
app.include_router(password_router)
app.include_router(follow_router)