from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

BASE_DIR = Path(__file__).parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", name="home", response_class=HTMLResponse)
async def home_page(request: Request) -> HTMLResponse:
    """
    Renders the home page using the 'home.html' template.

    Args:
        request (Request): The incoming HTTP request object.

    Returns:
        HTMLResponse: The rendered HTML response for the home page.
    """
    return templates.TemplateResponse(request, "home.html")
