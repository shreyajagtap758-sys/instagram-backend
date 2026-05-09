# api
from fastapi import FastAPI


from server.src.routes.follow import follow_router
from server.src.routes.password import password_router
from server.src.routes.user import user_router
from server.src.routes.posts import post_router


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
app.include_router(post_router)