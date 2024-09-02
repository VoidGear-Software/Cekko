import fastapi
from starlette.requests import Request
from starlette.templating import Jinja2Templates

router = fastapi.APIRouter(prefix="/story", tags=["story"])
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def story(request: Request, software_id: str) -> templates.TemplateResponse:
    storys = ["story1", "story2", "story3", "story4", "story5"]
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"Software ID {software_id}",
            "details2": "Storys: " + ", ".join(storys)
        }
    )


@router.get("/{story_id}")
async def story_part(request: Request, software_id: str, story_id: str) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"Software ID {software_id}",
            "details2": story_id
        }
    )
