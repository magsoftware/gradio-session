# FastAPI + Gradio Session Template

See: [Article on medium.com](https://medium.com/@marek.gmyrek/gradio-from-prototype-to-production-secure-scalable-gradio-apps-for-data-scientists-739cebaf669b)

## Introduction

This project is a robust template for building modern web applications using **FastAPI** and **Gradio**.
It provides a ready-to-use structure for secure user authentication, session management, and a modular
UI with a HomePage and multiple tabs. The template is designed for extensibility, maintainability,
and production-readiness, featuring middleware for authentication (JWT), HTTP session handling, and
request logging. The default session backend is an in-memory store, but the architecture allows
easy replacement with Redis or other backends.

## Quick Start

Get the application up and running in minutes:

### Step 1: Install Dependencies

Install all required dependencies using `uv`:

```bash
uv sync
```

This will:
- Create a virtual environment (if not exists)
- Install all project dependencies
- Install development dependencies (pytest, etc.)

### Step 2: Create Environment File

Create a `.env` file in the project root with the following variables:

```bash
# Required: JWT secret key (minimum 32 characters)
JWT_SECRET=your-super-secret-jwt-key-minimum-32-characters-long

# Required: Application metadata
VERSION=0.1.0
PROJECTNAME=Gradio App

# Optional: Secret keys for CSRF protection
SECRET_KEY=your-secret-key-for-general-use
CSRF_SECRET=your-csrf-secret-key

# Optional: Development settings
RELOAD=false
HOME_AS_HTML=false
```

**Important:** The `JWT_SECRET` must be at least 32 characters long. Generate a secure secret:

```bash
# Generate a random 32+ character secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Run the Application

After setting up the environment variables, start the application:

```bash
uv run gradioapp
```

Or using the script directly (after installing the package):

```bash
gradioapp
```

The application will start on `http://0.0.0.0:8080` (or `http://localhost:8080`).

### Step 4: Access the Application

1. Open your browser and navigate to `http://localhost:8080`
2. You will be redirected to the login page
3. Use the default test credentials:
   - **Username:** `john@test.com`
   - **Password:** `secret`

Or:

   - **Username:** `jane@test.com`
   - **Password:** `secret`

4. After successful login, you'll be redirected to the Gradio interface at `/gradio`

### Development Mode

For development with auto-reload on code changes, set `RELOAD=true` in your `.env` file:

```bash
RELOAD=true
```

Then run the application - it will automatically reload when you modify the code.

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

### Detailed Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd gradio-session
```

2. **Install dependencies:**
```bash
uv sync
```

This installs all required packages and creates a virtual environment.

3. **Create `.env` file:**
```bash
# Create .env file with required variables
cat > .env << EOF
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
VERSION=0.1.0
PROJECTNAME=Gradio App
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
CSRF_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
RELOAD=false
EOF
```

Or manually create `.env` with:
```bash
JWT_SECRET=your-super-secret-jwt-key-minimum-32-characters-long
VERSION=0.1.0
PROJECTNAME=Gradio App
SECRET_KEY=your-secret-key
CSRF_SECRET=your-csrf-secret
RELOAD=false
```

## Running the Application

### Method 1: Using the Script Command (Recommended)

After installing the package, you can run the application using:

```bash
uv run gradioapp
```

Or if the package is installed in your environment:

```bash
gradioapp
```

### Method 2: Using Python Module

```bash
uv run python -m gradioapp.main
```

### Method 3: Using Uvicorn Directly

```bash
uv run uvicorn gradioapp.main:app --host 0.0.0.0 --port 8080
```

### Development Mode

Set `RELOAD=true` in your `.env` file to enable auto-reload during development:

```bash
RELOAD=true
```

Then run the application - it will automatically reload when you modify the code.

## Default Credentials

The application comes with sample users for testing:

- **Username:** `john@test.com` / **Password:** `secret`
- **Username:** `jane@test.com` / **Password:** `secret`

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

## Development Tools

### Testing

Run the test suite:

```bash
uv run pytest tests/
```

Run tests with verbose output:

```bash
uv run pytest tests/ -v
```

Run tests with coverage:

```bash
uv run pytest tests/ --cov=gradioapp --cov-report=html
```

Run a specific test file:

```bash
uv run pytest tests/test_auth.py -v
```

Run a specific test class or function:

```bash
uv run pytest tests/test_auth.py::TestCreateAccessToken -v
```

### Code Formatting and Linting

#### Ruff

Ruff is used for import sorting and code formatting.

Check import sorting:

```bash
uv run ruff check src/gradioapp --select I
```

Fix import sorting automatically:

```bash
uv run ruff check --fix src/gradioapp --select I
```

Check code formatting:

```bash
uv run ruff format --check src/gradioapp
```

Format code automatically:

```bash
uv run ruff format src/gradioapp
```

#### Pylint

Pylint is used for code quality checking.

Run pylint on all source files:

```bash
uv run pylint src/gradioapp
```

Run pylint with specific output format:

```bash
uv run pylint src/gradioapp --output-format=text
```

Run pylint on a specific file:

```bash
uv run pylint src/gradioapp/main.py
```

The project is configured to achieve a 10.00/10 pylint score. Configuration is in `pyproject.toml` under `[tool.pylint]`.

#### Pyright

Pyright is used for static type checking to verify type hints and catch type-related errors.

Run pyright on all source files:

```bash
uv run pyright src/gradioapp
```

Run pyright on a specific file:

```bash
uv run pyright src/gradioapp/main.py
```

Run pyright with JSON output:

```bash
uv run pyright src/gradioapp --outputjson
```

The project uses type hints extensively (TypedDict, Protocol, union types) and pyright helps ensure type safety. Configuration is in `pyproject.toml` under `[tool.pyright]`.


## Summary

This template provides a solid foundation for building secure, scalable web applications
with FastAPI and Gradio. It features modular UI construction, robust session management,
layered middleware for security and observability, and a clean separation of concerns in
the codebase. You can easily extend it with new pages, authentication methods, or session
backends to fit your project's needs.
