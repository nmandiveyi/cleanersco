from fastapi.routing import APIRouter
from web.api import users
from web.api import job

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["User API"])
router.include_router(job.router, prefix="/job", tags=["Job API"])
