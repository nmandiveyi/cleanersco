from pydantic import BaseModel


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    hash: str


class LoginPayload(BaseModel):
    email: str
    password: str


class GetUserPayload(BaseModel):
    token: str


class TokenPayload(BaseModel):
    token: str
