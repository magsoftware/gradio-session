from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", name="home", response_class=HTMLResponse)
async def home_page(request: Request) -> HTMLResponse:
    """
    Renders the home page using the 'home.html' template.

    Args:
        request (Request): The incoming HTTP request object.

    Returns:
        HTMLResponse: The rendered HTML response for the home page.
    """
    return templates.TemplateResponse("home.html", {"request": request})
