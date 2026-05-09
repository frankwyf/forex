# Contributing Guide

Thank you for your interest in contributing to Forex Local Visual.

## Ways to Contribute

- Report bugs and suggest features through Issues
- Improve code quality and documentation
- Add tests and improve reliability
- Propose architecture or performance optimizations

## Development Setup

1. Create and activate virtual environment.

```powershell
cd forex\forex
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Configure environment variables.

```powershell
Copy-Item .env.example .env
```

4. Run local checks.

```powershell
python manage.py check
python manage.py migrate --noinput
```

## Branching and Pull Requests

1. Fork this repository and create a branch from main.
2. Use clear branch names, such as feat/scheduler-cleanup or fix/import-bug.
3. Keep each pull request focused on one concern.
4. Add context in PR description: problem, solution, validation steps.
5. Include screenshots when UI behavior changes.

## Code Style

- Follow existing project style and naming patterns.
- Prefer small, focused functions.
- Keep comments concise and meaningful.
- Avoid introducing unrelated refactors in the same PR.

## Commit Messages

Use clear commit messages. Example:

- feat: add scheduler startup guard for migrate command
- fix: handle missing apscheduler table before first migration
- docs: add multilingual open-source documentation

## Testing Expectations

Before opening a PR, run:

```powershell
python manage.py check
python manage.py migrate --noinput
```

If you add data or scheduler logic, explain how you validated behavior.

## Security and Sensitive Data

Do not commit:

- .env files
- local db.sqlite3
- logs and generated CSV data
- secrets, tokens, or credentials

Please review SECURITY.md before reporting vulnerabilities.

## Communication

Be respectful and constructive in all interactions. By participating, you agree to follow CODE_OF_CONDUCT.md.
