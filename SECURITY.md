# Security Policy

## Supported Versions

Security fixes target the latest 0.2.x release and the default branch. This is a local research application; public deployment needs a separate security review.

| Version | Supported |
| ------- | --------- |
| main    | Yes       |
| 0.2.x (latest patch) | Yes |
| 0.1.x | No |

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

1. Acknowledge report receipt on a best-effort basis (no response SLA is promised).
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
- With DEBUG=False the application rejects weak/default secrets and missing/wildcard hosts, and enables secure cookies and HTTPS redirects.
- Never expose runserver as a production service. Configure TLS/proxies, production hosting, backups, access controls and rate limits before public use.
- Tests use isolated settings and block network access through scripts/verify.py. Demo data is synthetic and must use a separate empty database.
