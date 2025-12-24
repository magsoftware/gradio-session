# Project Structure

> This document defines mandatory project conventions.
> These rules apply to both human contributors and AI-generated code.

## Directory Layout

- `src/gradioapp/` - Source code
  - `api/` - API routes and middleware
  - `domain/` - Business logic
  - `core/` - Core utilities
  - `ui/` - UI components
- `tests/` - Test files
- `docs/` - Documentation

## Import Style

- Use absolute imports from `gradioapp`
- Group imports: standard library, third-party, local
