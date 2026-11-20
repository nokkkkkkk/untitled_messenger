import random
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(request, "home.html")

@router.post("/join_chat")
async def join_chat(request: Request):
    form = await request.form()
    username = form.get("username")
    room_id = form.get("room_id")
    user_id = random.randint(1000, 9999)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "username": username,
            "room_id": room_id,
            "user_id": user_id,
        },
    )
