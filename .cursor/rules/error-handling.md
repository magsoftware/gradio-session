# Error Handling

> This document defines mandatory project conventions.
> These rules apply to both human contributors and AI-generated code.

## Exception Handling

- Use `try/except` blocks in middleware for exception catching
- Always re-raise exceptions after logging: `logger.exception(...); raise`
- Let exceptions propagate to FastAPI's error handlers

## Error Responses

- **401 Unauthorized**: Use `create_unauthorized_response(request, error_message)`
  - Browser requests → RedirectResponse (302) to `/login`
  - API requests → JSONResponse (401) with `{"error": "...", "redirect_to": "/login"}`
- **Validation Errors**: Return HTMLResponse with error message in template context
- **CSRF Errors**: Redirect to login with error query parameter

## Logging Levels for Errors

- **WARNING**: For validation failures, missing tokens, invalid credentials
  - Example: `logger.warning("Login form validation failed: {error}")`
- **EXCEPTION**: For unexpected errors in middleware
  - Use `logger.exception()` to log full traceback
  - Include context: method, path, user_id, session_id, duration

## Error Messages

- Keep error messages user-friendly but not too verbose
- Don't expose internal implementation details
- Use consistent error message format

## Middleware Error Handling

- LoggingMiddleware catches all exceptions and logs them
- Always include request context (method, path, user_id, session_id)
- Log duration of request before exception occurred
