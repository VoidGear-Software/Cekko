from fastapi import APIRouter

from ..schemas import User
from ..crud import create_user

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create")
async def create_user(user: User):
    await create_user(user)
