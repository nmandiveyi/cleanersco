import binascii
import typing
from fastapi import FastAPI, HTTPException, status
import jwt
from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Receive, Scope, Send
from models.user import User
from config import settings
from starlette.requests import HTTPConnection
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    UnauthenticatedUser,
)


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        backend: AuthenticationBackend,
        on_error: typing.Callable[[HTTPConnection, AuthenticationError], Response]
        | None = None,
    ):
        self.app = app
        self.backend = backend
        self.on_error = on_error

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        supported_scopes = {"http", "websocket"}
        if scope["type"] not in supported_scopes or "user" in scope["path"]:
            await self.app(scope, receive, send)
            return

        conn = HTTPConnection(scope)
        try:
            auth_result = await self.backend.authenticate(conn)
        except AuthenticationError as exc:
            response = self.on_error(conn, exc)
            if scope["type"] == "websocket":
                await send({"type": "websocket.close", "code": 1000})
            else:
                await response(scope, receive, send)
            return

        if auth_result is None:
            auth_result = AuthCredentials(), UnauthenticatedUser()
        scope["auth"], scope["user"] = auth_result
        await self.app(scope, receive, send)


class BasicAuth(AuthenticationBackend):
    async def authenticate(
        self,
        request: HTTPConnection,
    ) -> tuple[AuthCredentials, User] | None:
        if "Authorization" not in request.headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Missing auth params"
            )

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme != "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Authentication Error: Invalid auth scheme"
                )
            print(credentials, "Credentials.......", type(credentials))
            if not credentials or credentials == "null":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Authentication Error: Missing auth token"
                )
            decoded = jwt.decode(
                jwt=credentials,
                key=settings.secret,
                algorithms=[settings.jwt_algorithm],
                options = {
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_nbf': False,
                    'verify_iat': True,
                    'verify_aud': False
                }
            )
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid basic auth credentials")

        user = User(
            first_name=decoded.get("first_name", None),
            last_name=decoded.get("last_name", None),
            email=decoded.get("email", None),
            hash=None
        )
        return AuthCredentials([credentials]), user
