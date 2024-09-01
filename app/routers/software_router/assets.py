import fastapi
from starlette.requests import Request
from starlette.templating import Jinja2Templates

router = fastapi.APIRouter(prefix="/assets", tags=["assets"])
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def assets(request: Request, software_id: str) -> templates.TemplateResponse:
    assets = ["img1", "img2", "img3", "img4", "img5"]
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"Software ID {software_id}",
            "details2": "Assets: " + ", ".join(assets)
        }
    )


@router.get("/{asset_id}")
async def asset(request: Request, software_id: str, asset_id: str) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"Software ID {software_id}",
            "details2": f"Assets ID: {asset_id}"
        }
    )
