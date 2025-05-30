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


@router.get("/login", name="login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": None, "csrf_token": csrf_token}
    )


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
) -> Any:
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


@router.get("/logout", name="logout")
async def logout(request: Request) -> RedirectResponse:
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
