# Contributing

Use Python 3.12 (3.13 is also tested on Linux) and a repository-local .venv. Install with python -m pip install -r requirements.txt. The [README](README.md) covers macOS/Linux and Windows; external-SSD users should first apply [storage configuration](docs/macos-development.md).

## Before changing code

1. Start a focused branch from main and describe the user-visible problem.
2. Reproduce data loss, API failures or other substantial bugs with synthetic fixtures.
3. Make the smallest cohesive change and update its data contract and documentation.
4. Run python -m pip check and python scripts/verify.py.
5. Open a PR with the problem, resulting behavior and verification evidence.

The verifier uses disposable SQLite files and never loads your local .env or normal database. Python socket connections and live yfinance entry points are blocked during tests. Mock provider calls and clocks; do not download market data in CI. Never start a long-running collector to verify a test.

## Data changes

Validation must finish before replacing stored data. Database errors must roll back the entire replacement. Test missing providers, malformed and empty data, invalid timestamps/prices, duplicate and overlapping batches, and partial database writes.

Do not add a schema constraint or remove stored rows without an explicit compatibility analysis and a backup/recovery plan. Existing databases may contain duplicates. Explain migrations in the PR; irreversible changes require operator review.

## Dependencies and style

Retain pip and the existing requirements/constraints workflow. Update constraints in a reviewed dependency PR and let the full OS/Python matrix validate it. Keep functions focused and prefer pathlib, UTF-8 and timezone-aware UTC timestamps. Avoid unrelated formatting churn.

GitHub Actions revisions are pinned. Dependabot opens dependency and action updates for review; it does not auto-merge them.

## Reviews and releases

Use clear commits, include evidence in the PR, and wait for CI before merging. Version changes follow pre-1.0 semantic versioning. [Release instructions](docs/releasing.md) describe tag/version validation and source archives.

Do not commit local .env files, databases, logs, environments, generated CSV batches, credentials or provider data. For vulnerabilities, follow [SECURITY.md](SECURITY.md). Participation follows the [code of conduct](CODE_OF_CONDUCT.md).
