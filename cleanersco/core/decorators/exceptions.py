import functools
from fastapi import HTTPException, status
from core.services.logger import logger

def catch_server_err(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error("Internal Server Error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal Server Error. Detail: {e}"
            )
    return wrapper