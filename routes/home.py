from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", name="home", response_class=HTMLResponse)
async def home_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("home.html", {"request": request})
