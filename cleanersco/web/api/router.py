from fastapi.routing import APIRouter
from web.api import users

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["User API"])
