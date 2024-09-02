import fastapi
from starlette.requests import Request

router = fastapi.APIRouter(prefix="/files", tags=["files"])


@router.get("/")
async def index(request: Request):
    return {"message": "poc", "request": request}
