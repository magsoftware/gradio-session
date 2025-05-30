from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from services import (
    authenticate_user,
    create_session_token,
    generate_csrf_token,
    validate_csrf_token,
    verify_token,
)
from session import get_session_store

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/login", name="login", response_class=HTMLResponse, response_model=None)
async def login_page(request: Request) -> HTMLResponse:
    """
    Renders the login page with a CSRF token.

    Args:
        request (Request): The incoming HTTP request object.

    Returns:
        HTMLResponse: The rendered login page with a CSRF token included in the context.
    """
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": None, "csrf_token": csrf_token}
    )


@router.post("/login", response_model=None)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
) -> RedirectResponse | HTMLResponse:
    """
    Handles user login by validating CSRF token, authenticating credentials, and creating a session.

    Args:
        request (Request): The incoming HTTP request object.
        username (str): The username submitted via form data.
        password (str): The password submitted via form data.
        csrf_token (str): The CSRF token submitted via form data.

    Returns:
        HTMLResponse: 
            - If CSRF token is invalid, returns a rendered login template with an error message.
            - If authentication fails, returns a rendered login template with an error message.
        RedirectResponse:
            - If authentication is successful, creates a session, sets an access token cookie,
              and redirects to '/gradio'.
    """
    if not validate_csrf_token(csrf_token, request):
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid CSRF token"}
        )
    user = authenticate_user(username, password)
    if user:
        access_token, session_id = create_session_token(
            username, expires_delta=timedelta(minutes=30)
        )
        get_session_store().create_session(
            session_id=session_id, username=user.username, data={}
        )
        response = RedirectResponse(url="/gradio", status_code=302)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        logger.info(
            f"Login: user={user.username} successfully logged in, session_id={session_id}"
        )

        return response

    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid credentials"}
    )


@router.get("/logout", name="logout", response_class=RedirectResponse, response_model=None)
async def logout(request: Request) -> RedirectResponse:
    """
    Logs out the current user by invalidating their session and removing the access token cookie.

    This function retrieves the access token from the request cookies, verifies it, and if valid,
    invalidates the associated session in the session store. It then redirects the user to the login
    page and deletes the access token cookie from the response.

    Args:
        request (Request): The incoming HTTP request containing cookies.

    Returns:
        RedirectResponse: A redirect response to the login page with the access token cookie deleted.
    """
    token = request.cookies.get("access_token")
    if token:
        payload = verify_token(token)
        if payload:
            # Invalidate the session
            session_id = payload.get("session_id")
            get_session_store().delete_session(session_id)
            logger.info(
                f"Logout: session {session_id} for the user {payload.get('sub')} invalidated"
            )

    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")

    logger.info("Logout: user successfully logged out")
    return response
