# Logging

> This document defines mandatory project conventions.
> These rules apply to both human contributors and AI-generated code.

## Logger

- Use `loguru` logger: `from loguru import logger`
- Logger is configured in `core/logging.py` with custom format

## Log Levels

- **DEBUG**: Routine operations, request processing, session operations
  - Example: `logger.debug("Processing request: {method} {path}")`
  - Example: `logger.debug("Session found for session_id: {id}")`
- **INFO**: Important business events (login, logout, initialization)
  - Example: `logger.info("Login: user={username} successfully logged in")`
  - Example: `logger.info("Logging initialized with custom format")`
- **WARNING**: Validation failures, missing data, invalid tokens
  - Example: `logger.warning("No access token found. Redirecting to /login.")`
  - Example: `logger.warning("Login form validation failed: {error}")`
- **ERROR**: Not currently used (exceptions use EXCEPTION level)
- **EXCEPTION**: Unexpected errors with full traceback
  - Use `logger.exception()` in exception handlers
  - Include context: method, path, user_id, session_id, duration

## Log Format

- Format includes: timestamp, level, location (module:function:line), message
- Location is truncated/padded to 40 characters
- Example: `2025-12-24 23:10:00 | DEBUG    | gradioapp.api.middleware.auth:dispatch:37 - Processing request: GET /login`

## Logging Best Practices

- Log at appropriate level (DEBUG for routine, INFO for important events)
- Include relevant context (user_id, session_id, request path)
- Don't log sensitive data (passwords, tokens)
- Use structured logging when possible (key=value format)
- Log exceptions with full context before re-raising

## Middleware Logging

- LoggingMiddleware logs all requests with:
  - Method and path
  - Response status code
  - User ID and session ID
  - Request duration in milliseconds
- Logs exceptions with same context

