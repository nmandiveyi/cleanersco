import uvicorn
from config import settings


def main():
    uvicorn.run(
        "web.app:get_application",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=settings.reload,
        workers=settings.workers,
        factory=settings.factory,
    )


if __name__ == "__main__":
    main()
