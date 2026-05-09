# Security Policy

## Supported Versions

This project is currently maintained on the default branch.

| Version | Supported |
| ------- | --------- |
| main    | Yes       |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

Preferred process:

1. Do not open a public issue with exploit details.
2. Contact maintainers through a private channel.
3. Provide clear reproduction steps, impact, and affected files.
4. Allow maintainers a reasonable time to investigate and patch.

If no private channel is available yet, open a minimal public issue requesting a secure contact path without disclosing sensitive details.

## Response Process

Maintainers will try to:

1. Acknowledge report receipt within 3 business days.
2. Triage and assess impact.
3. Prepare and validate a fix.
4. Publish a coordinated advisory when appropriate.

## Security Best Practices for Contributors

- Never commit secrets or credentials.
- Keep dependencies up to date.
- Validate and sanitize external data.
- Use environment variables for runtime secrets.
- Avoid logging sensitive values.

## Project-Specific Notes

- This repository ignores local runtime artifacts such as db.sqlite3, logs, and generated CSV files.
- Use DJANGO_SECRET_KEY from environment variables in non-local environments.
