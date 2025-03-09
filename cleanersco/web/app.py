from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse
from contextlib import asynccontextmanager

from core.services.auth import AuthMiddleware, BasicAuth
from core.services.logger import Logger, RequestLoggingMiddleware
from utils.docs import attach_api_doc_routes
from web.api.router import router
from core.services.db import prisma


api_prefix = "/api/v1"


def get_application() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await prisma.connect()
        yield
        await prisma.disconnect()

    Logger.setup_logger()
    app = FastAPI(
        openapi_url=f"{api_prefix}/openapi.json",
        default_response_class=UJSONResponse,
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )

    app.include_router(
        prefix=api_prefix,
        router=router,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        RequestLoggingMiddleware,
    )

    app.add_middleware(AuthMiddleware, backend=BasicAuth())

    attach_api_doc_routes(app)
    return app
