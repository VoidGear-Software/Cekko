import fastapi
from starlette.requests import Request
from starlette.templating import Jinja2Templates

router = fastapi.APIRouter(prefix="/characters", tags=["characters"])
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def characters(request: Request, software_id: str) -> templates.TemplateResponse:
    characters = ["char1", "char2", "char3", "char4", "char5"]
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"Software ID {software_id}",
            "details2": "Character: " + ", ".join(characters)
        }
    )


@router.get("/{character_id}")
async def character(request: Request, software_id: str, character_id: str) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"Software ID {software_id}",
            "details2": f"Character: {character_id}"
        }
    )
