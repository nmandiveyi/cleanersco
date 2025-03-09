from fastapi import APIRouter
from services.user import UserService
from models.user import GetUserPayload, LoginPayload, TokenPayload, User

router = APIRouter()

@router.post("")
async def get_user(payload: GetUserPayload) -> User:
    return await UserService.get_user(payload.token)


@router.post("/signup")
async def signup_user(payload: User) -> User:
    return await UserService.signup_user(payload)


@router.post("/login")
async def login_user(payload: LoginPayload) -> TokenPayload:
    return await UserService.login_user(payload)
