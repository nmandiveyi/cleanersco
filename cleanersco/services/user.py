from time import time
from bcrypt import checkpw, gensalt, hashpw
from models.user import LoginPayload, TokenPayload, User
from core.services.db import prisma
from config import settings
import jwt
from fastapi import HTTPException, status


class UserService:
    @staticmethod
    async def signup_user(payload: User) -> None:
        salt = gensalt()
        payload.hash = hashpw(payload.hash.encode(), salt).decode()
        await prisma.user.create(data=payload.model_dump())
        return payload

    async def get_user(token: str) -> User:
        token_payload = jwt.decode(jwt=token, key=settings.secret, algorithms=["HS256"])
        return await prisma.user.find_first(
            where={"email": token_payload.get("email", None)}
        )

    async def login_user(payload: LoginPayload):
        user = await prisma.user.find_first(where={"email": payload.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )

        stored_pw = user.hash.encode()
        provided_pw = payload.password.encode()

        valid_password = checkpw(provided_pw, stored_pw)

        if valid_password:
            token = jwt.encode(
                payload={
                    "sub": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "iat": time(),
                    "exp": time() + settings.jwt_token_duration,
                },
                key=settings.secret,
                algorithm=settings.jwt_algorithm,
            )
            return TokenPayload(token=token)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )
