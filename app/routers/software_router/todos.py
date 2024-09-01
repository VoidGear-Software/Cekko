import fastapi
from starlette.requests import Request
from starlette.templating import Jinja2Templates

router = fastapi.APIRouter(prefix="/todos", tags=["todos"])
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def software_todos(request: Request, software_id: str) -> templates.TemplateResponse:
    todos = ["todo1", "todo2", "todo3", "todo4", "todo5"]
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"Software ID {software_id}",
            "details2": "Todos: " + ", ".join(todos)
        }
    )


@router.get("/{todo_id}")
async def todo(request: Request, software_id: str, todo_id: str) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"Software ID {software_id}",
            "details2": f"Todo ID: {todo_id}"
        }
    )
