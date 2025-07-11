
## Abstract 🚀

This article introduces Gradio‑Session, a framework that combines FastAPI and Gradio to support production‑ready web apps for data scientists and ML practitioners. It provides full user authentication, JWT‑based authorization, and flexible session state management—far beyond Gradio's built‑in gr.State. Both authentication and session state are handled outside Gradio, enabling stateless scaling and pluggable storage backends (e.g. in‑memory, Redis, SQL). The goal is to empower teams to build secure, scalable Gradio interfaces backed by robust infrastructure.

## Problem Statement

Gradio is a fantastic rapid‑prototyping UI framework. However, for production applications, its built‑in mechanisms for authentication and state (gr.State, gr.BrowserState) are simplified and limited:

- No built‑in user management or login flows.
- gr.State resides within the Gradio process—leading to session conflicts, especially in multi‑user or multi‑server setups 
- Scaling Gradio horizontally is difficult when state is tied to one process.

These limitations become roadblocks when building multi‑tenant, secure dashboards or LLM‑powered applications.

## Proposed Solution
To overcome the limitations of Gradio’s built-in state and authentication mechanisms, the Gradio‑Session framework introduces a more modular and scalable approach that integrates FastAPI with external session handling. The solution is built on three core pillars:

### Architecture

```
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

### Authentication Powered by FastAPI
Instead of relying on any client-side or simplistic user identification methods, Gradio‑Session uses FastAPI to implement robust user authentication workflows. These include fully functional login and registration endpoints that issue JWT tokens upon successful authentication. These tokens encode essential information like the user_id and a unique session_id, and serve as the foundation for secure, stateless user identification. Additionally, the framework supports role-based access control, enabling fine-grained permissions linked to users stored in a JSON file or a more scalable SQL database.

```
┌───────────────┐
│ JWT Token     │
│ ┌───────────┐ │
│ │ session_id│ │◀───┐
│ │ user_id   │ │    │
│ └───────────┘ │    │
└───────────────┘    │
                     ▼
        ┌────────────────────────┐
        │ sessions (in Redis /   │
        │ in‑memory dict)        │
        │ { session_id: { ... }  │
        └────────────────────────┘

```

This approach separates user management logic from the Gradio interface entirely, providing a clean and secure backend layer that can evolve independently of the UI.

### Decoupled and Pluggable Session Management
Gradio‑Session moves beyond the constraints of gr.State by managing user sessions outside the Gradio runtime. Instead of holding transient state in the frontend, session data is bound to the session_id (encoded in JWT) and stored in a Python dictionary by default. This external store behaves like a simple in-memory key-value database, where each session ID maps to a dictionary of arbitrary data.

What makes this solution powerful is its pluggability. The session layer is abstracted in such a way that developers can swap the in-memory implementation for production-grade alternatives like Redis, SQL, or any other backend. This design allows applications to remain stateless, significantly simplifying scaling across multiple processes or containers in distributed environments.

```
┌──────────────────────────────┐
│    InMemorySessionStore      │
│     (self._store: dict)      │
└──────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────┐
│   session_id (str)     |         session data          │
├────────────────────────┬───────────────────────────────┤
│      "sess10"          │    {"data": {...},            |
|                        |     "username": user1         │
│                        │     "expire_at": <timestamp>} │
├────────────────────────┼───────────────────────────────┤
│      "sess11"          │    {"data": {...},            │
|                        |     "username": user2         │
│                        │     "expire_at": <timestamp>} │
└────────────────────────┴───────────────────────────────┘
```

### Seamless Session Injection into Gradio
While FastAPI handles authentication and session storage, Gradio‑Session ensures that each user’s session data is made available to Gradio component callbacks through middleware. When a request reaches the application, FastAPI middleware extracts the JWT from the headers, decodes the token, and retrieves the associated session. This session is then injected into the Gradio function handlers as a regular Python dictionary.

This mechanism allows Gradio apps to easily implement features like user-specific history, model inputs/outputs, preferences, or any stateful interaction—without depending on browser-local or frontend-managed storage. It preserves the simplicity of writing Gradio interfaces while adding the robustness of enterprise-ready session logic.

### Request flow

```
[ User ] → [ FastAPI ˙JWT auth˙ ] → [ Session Store ]
                         │
                         └── mounts → [ Gradio App ]
                                 ↕️ session access via middleware ──→ Gradio component functions

```

## Implementation andKey Modules

### Directory structure

```
.
├── core
│   ├── __init__.py
│   ├── logging.py
│   └── session.py
├── main.py
├── middleware
│   ├── __init__.py
│   ├── auth.py
│   ├── logging.py
│   ├── session.py
│   └── utils.py
├── pyproject.toml
├── README.md
├── routes
│   ├── __init__.py
│   ├── health.py
│   ├── home.py
│   ├── login.py
│   └── static.py
├── services
│   ├── __init__.py
│   ├── auth.py
│   ├── csrf.py
│   └── database.py
├── session
│   ├── __init__.py
│   ├── database_session.py
│   ├── inmemory_session.py
│   ├── redis_session.py
│   └── session_store.py
├── settings
│   ├── __init__.py
│   └── base.py
├── static
│   └── manifest.json
├── templates
│   ├── base.html
│   ├── home.html
│   └── login.html
├── ui
│   ├── __init__.py
│   ├── gradio_app.py
│   ├── javascript.py
│   ├── navbar.py
│   └── pages
│       ├── __init__.py
│       ├── base_page.py
│       ├── base_tab.py
│       └── home_page.py
└── uv.lock
```

#### core/
Contains core utilities and abstractions:

- logging.py: Loguru custom logging setup.
- session.py: Helper functions for session management.

#### middleware/
FastAPI middleware logic:

- auth.py: JWT extraction and validation middleware.
- session.py: Injects session context into requests.
- logging.py: Request/response logging hooks.

#### routes/
Defines API endpoints (as FastAPI routers):

- login.py: Handles login/logout process.
- home.py: Base routes for the homepage (not used).
- health.py: Health-check endpoint.
- static.py: Serves static files (`/manifest.json`)

#### services/
Encapsulates reusable services and integrations:

- auth.py: Authentication logic, JWT token creation and verification.
- csrf.py: CSRF protection utilities (for the login form).
- database.py: Abstraction for user database access (here simple Python dictionary, can be replaced by any other production implementation).

#### session/
Plug-and-play session backends:

- session_store.py: Unified interface, Python Protocol class.
- inmemory_session.py: Default in-memory implementation.
- redis_session.py: Redis-backed session store (empty implementation).
- database_session.py: SQL session store (empty implementation).

#### ui/
Gradio UI logic:

- gradio_app.py: Main Gradio interface (with mounting logic).
- navbar.py: Reusable navigation components.
- javascript.py: Custom JS scripts. Defines fetch interceptor for handling 401 Unauthorized responses. Eg. if the user's session expires, we return 401 and this interceptor is responsible for redirecting the user to the login page.

#### ui/pages/

Individual pages or tabs like home_page.py, base_page.py.

#### settings/
Centralized app configuration:

- base.py: App settings, environment flags, secrets.

#### templates/ and static/
Used for rendering HTML responses via Jinja2 (outside Gradio), and static assets (e.g. manifest.json for frontend).

#### root Files:
`main.py`: App entry point:

- configurec Loguru logging,
- initializes session store (InMemorySessionStore),
- sets up FastAPI,
- adds middlware for authenticatio, session and logging,
- mounts all routes,
- mounts Gradio application,
- starts the application.

The architecture of Gradio‑Session is deliberately modular, making it easy to understand, extend, and maintain. Each component serves a specific purpose—from user authentication to session persistence—working together to provide a robust backend environment for Gradio-based applications. Below is a closer look at the core modules and how they contribute to the overall system.

### Authentication and Authorization Layer
This module handles the entire lifecycle of user authentication. It defines FastAPI routes for login and logout. When a user successfully logs in, a JWT token is generated, containing claims like user_id, session_id, and expiration metadata.

The authentication logic also supports role-based access control, which is essential for applications that require permission levels (e.g. admin vs. user). User credentials are initially stored in a JSON file for simplicity, but the design supports swapping this out for SQL or any persistent data store. Passwords are securely hashed, typically using bcrypt, ensuring that even in simple setups, security is taken seriously.

By isolating this logic from the UI, the application achieves a clean separation of concerns and aligns with best practices in modern web security.

### Stateless Session Management
Session handling is abstracted into its own module to promote flexibility and scalability. At its core is a session store—by default, a Python dictionary mapping session_id values to individual session states (themselves represented as dictionaries).

This setup allows you to store arbitrary user-specific data like model inputs, conversation history, user preferences, or application state between interactions.

Importantly, the session layer is designed to be backend-agnostic. Session store interface is defined as Python Protocol class. You can replace the default in-memory dictionary with a persistent store like Redis, which is ideal for high-concurrency or distributed deployments. This external session handling decouples the application state from Gradio’s internal state mechanisms, making the entire system inherently stateless and cloud-native.

### Middleware and User Context Injection
To make session and user data accessible across the app, Gradio‑Session uses FastAPI middleware. Every incoming request is intercepted, and the middleware extracts and decodes the JWT token from the cookie.

Based on the decoded token, it reconstructs the session using the session backend and attaches it to the request’s state. This makes user identity and session information available to every downstream route or component—including Gradio callback functions—without explicitly passing them through the UI.

This layer plays a crucial role in securely and efficiently bridging authentication with session logic.

### Gradio UI with Stateful Handlers
Here is where data science meets user experience. This module defines the actual Gradio interface using gr.Blocks or gr.Interface, just as in any standard Gradio app. The key difference is that function handlers are now capable of receiving the session dictionary, which is automatically injected by the middleware.

This allows the creation of dynamic, personalized applications where each user’s interaction history is preserved independently—without relying on browser state or cookies.

### main.py – Application Orchestration and Mounting
This is the main entry point of the application. It sets up the FastAPI instance, registers authentication and session-related endpoints, and mounts the Gradio interface onto a specific route (e.g. /gradio). This central file effectively wires together all other modules and defines how the app behaves when deployed.

It also ensures that the Gradio UI inherits all of FastAPI’s middleware, routing, and security features—making it a first-class citizen in the backend architecture.

This modular design not only improves maintainability and clarity but also enables advanced use cases like:

- Persistent chatbots with per-user context
- Dashboards with user-specific data streams
- Role-protected admin views
- Seamless scale-out across containers or services


## Benefits

- Secure authentication using industry-standard JWT and FastAPI.
- Scalable stateless design: session data can live in Redis or a database.
- Multi‑user support: isolates sessions per user—no state conflicts.
- Flexible backend: simple in-memory for dev; Redis/SQL for prod.
- Natural integration: users write Gradio Blocks as usual, with session passed in.

## Summary
Gradio‑Session bridges the gap between easy ML UI prototyping and production‑grade web apps. It separates concerns: FastAPI manages access and session, Gradio consumes session context effortlessly. This enables deploying secure, concurrent, multi‑user dashboards or LLM‑powered services at scale.

The repository (https://github.com/magsoftware/gradio-session) includes:

- Example app with login/logout
- JWT middleware
- Pluggable session backends
- Usage examples with Gradio Blocks

For anyone building professional Gradio interfaces—like research dashboards or enterprise LLM apps—this framework provides the missing infrastructure layer.

You can try Gradio‑Session, reuse it in whole or in part and build your application with confidence.