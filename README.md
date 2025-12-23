# FastAPI + Gradio Session Template

See: [Article on medium.com](https://medium.com/@marek.gmyrek/gradio-from-prototype-to-production-secure-scalable-gradio-apps-for-data-scientists-739cebaf669b)

## Introduction

This project is a robust template for building modern web applications using **FastAPI** and **Gradio**.
It provides a ready-to-use structure for secure user authentication, session management, and a modular
UI with a HomePage and multiple tabs. The template is designed for extensibility, maintainability,
and production-readiness, featuring middleware for authentication (JWT), HTTP session handling, and
request logging. The default session backend is an in-memory store, but the architecture allows
easy replacement with Redis or other backends.

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd gradio-session
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env  # If you have an example file
# Or create .env with required variables:
# JWT_SECRET=<your-secret-key-min-32-chars>
# VERSION=0.1.0
# PROJECTNAME=Gradio App
# SECRET_KEY=<your-secret-key>
# CSRF_SECRET=<your-csrf-secret>
```

## Running the Application

### Using the Script Command

After installing the package, you can run the application using:

```bash
gradioapp
```

Or with uv:

```bash
uv run gradioapp
```

### Using Python Module

```bash
uv run python -m gradioapp.main
```

### Using Uvicorn Directly

```bash
uv run uvicorn gradioapp.main:app --host 0.0.0.0 --port 8080
```

### Development Mode

Set `RELOAD=true` in your `.env` file to enable auto-reload during development:

```bash
RELOAD=true
```

Then run the application - it will automatically reload on code changes.

## Default Credentials

The application comes with sample users for testing:

- Username: `john@test.com` / Password: `secret`
- Username: `jane@test.com` / Password: `secret`

## Project Structure

```
gradio-session/
├── src/
│   └── gradioapp/           # Main application package
│       ├── api/             # FastAPI layer (routes + middleware)
│       ├── domain/          # Business logic (auth, user, session)
│       ├── core/            # Core utilities
│       ├── ui/              # Gradio UI components
│       ├── config.py        # Application settings
│       └── main.py          # Application entry point
├── tests/                   # Test suite
├── docs/                    # Documentation
└── pyproject.toml          # Project configuration
```


## Architecture

```text
                       ┌────────────────────┐
                       │      User          │
                       └────────┬───────────┘
                                │
                      HTTP/WebSocket
                                │
                       ┌────────▼─────────┐
                       │   Load Balancer  │  ◄──── Sticky Sessions (optional)
                       └─────┬──────┬─────┘
                             │      │
                    ┌────────▼┐  ┌──▼────────┐
                    │ Gradio  │  │  Gradio   │  ◄──── Stateless (does not use in-memory gr.State)
                    │Instance │  │ Instance  │
                    └─────────┘  └───────-───┘
                          │            │
                          └────┬───────┘
                               │
                  ┌────────────▼────────────┐
                  │         Redis           │  ◄──── Stores user session/state
                  └─────────────────────────┘

                  ┌────────────┐   ┌────────────┐
                  │  Backend   │   │  Model API │  ◄──── Optional: model serving
                  └────────────┘   └────────────┘

                  ┌──────────────────────────────┐
                  │     Object Storage (S3, etc.)│  ◄──── Stores files, logs, data
                  └──────────────────────────────┘
```


## UI Interface (`src/gradioapp/ui` folder) and HomePage (`src/gradioapp/ui/pages` folder)

- The **`ui`** folder contains the logic for building the Gradio-based user interface. It includes:
  - Components for navigation and layout.
  - JavaScript interceptors for handling authentication redirects and enhancing UX.
  - The main entry point for the UI is a function (e.g., `create_gradio_app`) that assembles the Gradio Blocks interface.

- The **`ui/pages`** folder contains page definitions, including:
  - **HomePage**: The main protected page, typically with several tabs for different functionalities.
  - Each page is implemented as a class or function, making it easy to add new pages or tabs.


## Session Management (`src/gradioapp/domain/session` folder)

The **`domain/session`** folder provides infrastructure for managing user sessions. The class **`SessionStore`** is an
interface (Python Protocol), and defines the basic contract of the session store.

The default implementation is **`InMemorySessionStore`**, which keeps session data in a Python dictionary in
a memory of a running process.

Each session is identified by a unique `session_id` and stores user-specific data, including expiration timestamps.

The session store can be easily swapped for a persistent backend (e.g., Redis, any relational or NoSQL database) by
implementing the same interface. In this way we can have application state maintained in an external system and
thus make the application stateless and easily horizontally scalable.

Session initialization and cleanup are handled automatically, and session data is accessible throughout the request
lifecycle.

### Session Store Structure

```text
┌──────────────────────────────┐
│    InMemorySessionStore      │
│     (self._store: dict)      │
└──────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────┐
│   session_id (str)     |         session data          │
├────────────────────────┬───────────────────────────────┤
│      "abc123"          │    {"data": {...},            |
|                        |     "username": user1         │
│                        │     "expire_at": <timestamp>} │
├────────────────────────┼───────────────────────────────┤
│      "xyz789"          │    {"data": {...},            │
|                        |     "username": user2         │
│                        │     "expire_at": <timestamp>} │
└────────────────────────┴───────────────────────────────┘

Each "data" dict inside looks like:

data = {
    "custom1": { ... }  ← any session-specific data
    "custom2": { ... }  ← any session-specific data
}
```


## Middleware: Authentication, HTTP Sessions, Logging (`src/gradioapp/api/middleware` folder)

- **Authentication** Middleware (`auth.py`):
  - Verifies JWT tokens in cookies for protected routes.
  - Redirects unauthenticated users to the login page.
  - Extracts user information and session ID from the token and attaches it to the request state.

- **Session** Middleware (`session.py`):
  - Validates the presence and validity of the session ID.
  - Handles session expiration and cleanup.

- **Logging** Middleware (`logging.py`):
  - Logs each HTTP request with method, path, user/session info, status, and duration.
  - Captures and logs exceptions for easier debugging.

All middleware is registered in `main.py` and executed in a defined order.


## Endpoints (`src/gradioapp/api/routes` folder)

- The **`api/routes`** folder organizes all HTTP endpoints:
  - **`login.py`**: Handles GET/POST for user login, CSRF protection, and session creation.
  - **`home.py`**: Serves the main HomePage (protected).
  - **`health.py`**: Provides a health check endpoint (`/healthz`) for monitoring.
  - **`static.py`**: Serves static assets like manifest.json.

Each route is implemented as an APIRouter and included in the main FastAPI app. Endpoints
are protected by middleware as appropriate.

## Testing

Run the test suite:

```bash
uv run pytest tests/
```

Run tests with coverage:

```bash
uv run pytest tests/ --cov=gradioapp --cov-report=html
```


## Summary

This template provides a solid foundation for building secure, scalable web applications
with FastAPI and Gradio. It features modular UI construction, robust session management,
layered middleware for security and observability, and a clean separation of concerns in
the codebase. You can easily extend it with new pages, authentication methods, or session
backends to fit your project's needs.
