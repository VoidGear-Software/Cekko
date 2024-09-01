import fastapi
from starlette.requests import Request
from starlette.templating import Jinja2Templates

router = fastapi.APIRouter(prefix="/chat", tags=["chat"])
templates = Jinja2Templates(directory="templates")


@router.get("/software/{software_id}")
async def software_channels(request: Request, software_id: str) -> templates.TemplateResponse:
    channels = ["ch1", "ch2", "ch3", "ch4", "ch5"]
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"Software ID: {software_id}",
            "details2": "Channels: " + ", ".join(channels)
        }
    )


@router.get("/software/{software_id}/{channel_id}")
async def software_chat(request: Request, software_id: str, channel_id: str) -> templates.TemplateResponse:
    messages = ["msg1", "msg2", "msg3", "msg4", "msg5"]
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"Software ID: {software_id} \nChannel ID: {channel_id}",
            "details2": "Messages: " + ", ".join(messages)
        }
    )


@router.get("/user/{user_id}")
async def user_chat(request: Request, user_id: str) -> templates.TemplateResponse:
    messages = ["msg1", "msg2", "msg3", "msg4", "msg5"]
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"User ID: {user_id}",
            "details2": "Messages: " + ", ".join(messages)
        }
    )


@router.get("/group/{group_id}")
async def user_chat(request: Request, group_id: str):
    messages = ["msg1", "msg2", "msg3", "msg4", "msg5"]
    users = ["user1", "user2", "user3", "user4", "user5"]
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "details": f"Group ID: {group_id}",
            "details2": "Messages: " + ", ".join(messages) +
                        "\nUsers: " + ", ".join(users)
        }
    )
