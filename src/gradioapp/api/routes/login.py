from datetime import timedelta
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
from starlette.datastructures import URL

from ...domain.auth import create_session_token, verify_token
from ...domain.csrf import generate_csrf_token, validate_csrf_token
from ...domain.session.store import get_session_store
from ...domain.user import authenticate_user

router = APIRouter()

BASE_DIR = Path(__file__).parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Validation constants
MAX_USERNAME_LENGTH = 255
MAX_PASSWORD_LENGTH = 255
MIN_FIELD_LENGTH = 1


def validate_login_form(username: str, password: str, csrf_token: str) -> str | None:
    """
    Validate login form data.

    Args:
        username (str): The username to validate.
        password (str): The password to validate.
        csrf_token (str): The CSRF token to validate.

    Returns:
        str | None: Error message if validation fails, None otherwise.
    """
    if not username or len(username.strip()) < MIN_FIELD_LENGTH:
        return "Username is required"
    if len(username) > MAX_USERNAME_LENGTH:
        return f"Username must be at most {MAX_USERNAME_LENGTH} characters"
    if not password or len(password.strip()) < MIN_FIELD_LENGTH:
        return "Password is required"
    if len(password) > MAX_PASSWORD_LENGTH:
        return f"Password must be at most {MAX_PASSWORD_LENGTH} characters"
    if not csrf_token or len(csrf_token.strip()) < MIN_FIELD_LENGTH:
        return "CSRF token is required"
    return None


@router.get("/login", name="login", response_class=HTMLResponse, response_model=None)
async def login_page(request: Request, error: str | None = None) -> HTMLResponse:
    """
    Renders the login page with a CSRF token.

    Args:
        request (Request): The incoming HTTP request object.

    Returns:
        HTMLResponse: The rendered login page with a CSRF token included in the context.
    """
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse(
        request, "login.html", {"error": error, "csrf_token": csrf_token}
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
        username (str): The username submitted via form data (1-255 characters).
        password (str): The password submitted via form data (1-255 characters).
        csrf_token (str): The CSRF token submitted via form data.

    Returns:
        HTMLResponse:
            - If CSRF token is invalid, returns a rendered login template with an error message.
            - If authentication fails, returns a rendered login template with an error message.
            - If validation fails, returns a rendered login template with an error message.
        RedirectResponse:
            - If authentication is successful, creates a session, sets an access token cookie,
              and redirects to '/gradio'.
    """
    # Validate form data
    validation_error = validate_login_form(username, password, csrf_token)
    if validation_error:
        logger.warning(f"Login form validation failed: {validation_error}")
        return templates.TemplateResponse(
            request, "login.html", {"error": validation_error}
        )

    if not validate_csrf_token(csrf_token, request):
        url = URL("/login").include_query_params(error="Invalid CSRF token")
        return RedirectResponse(url, status_code=303)

    user = authenticate_user(username, password)
    if user:
        access_token, session_id = create_session_token(
            username, expires_delta=timedelta(minutes=30)
        )
        get_session_store().create_session(
            session_id=session_id, username=user.username, data={}
        )
        response = RedirectResponse(url="/gradio", status_code=302)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )
        logger.info(
            f"Login: user={user.username} successfully logged in, session_id={session_id}"
        )

        return response

    return templates.TemplateResponse(
        request, "login.html", {"error": "Invalid credentials"}
    )


@router.get(
    "/logout", name="logout", response_class=RedirectResponse, response_model=None
)
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
            if session_id:
                get_session_store().delete_session(session_id)
                logger.info(
                    f"Logout: session {session_id} for the user {payload.get('sub')} invalidated"
                )

    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token", secure=True, samesite="lax")

    logger.info("Logout: user successfully logged out")
    return response
