# Git Commands

> This document defines mandatory project conventions.
> These rules apply to both human contributors and AI-generated code.

When user says "zrob git add/commit" or "git add/cc", perform:

1. `git add .` (or specific files if mentioned)
2. `git commit -m "type: message"` using conventional commits
3. Ask for commit message if not provided

## Conventional Commits

Use these types:

- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes (formatting)
- refactor: Code refactoring
- perf: Performance improvements
- test: Adding or updating tests
- chore: Maintenance tasks
- build: Build system changes
- ci: CI/CD changes
