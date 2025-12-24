# Code Style

> This document defines mandatory project conventions.
> These rules apply to both human contributors and AI-generated code.

- Use type hints
- Follow PEP 8
- Use ruff for formatting and linting
- Run tests before committing

## Testing

- Run `uv run python -m pytest tests/ -v` before committing
- Ensure all tests pass
- Add tests for new features
