import fastapi
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from .software_router import asset_router, characters_router, story_router, todo_router

router = fastapi.APIRouter(prefix="/software", tags=["software"])
templates = Jinja2Templates(directory="templates")

router.include_router(asset_router, prefix="/{software_id}")
router.include_router(characters_router, prefix="/{software_id}")
router.include_router(story_router, prefix="/{software_id}")
router.include_router(todo_router, prefix="/{software_id}")


@router.get("/")
async def projects(request: Request) -> templates.TemplateResponse:
    software = ["sw1", "sw2", "sw3", "sw4", "sw5"]
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": "Projects: " + ", ".join(software)
        }
    )


@router.get("/{software_id}")
async def project(request: Request, software_id: str) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"Software: {software_id}"
        }
    )
