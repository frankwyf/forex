# Forex Local Visual

[![CI](https://github.com/frankwyf/forex/actions/workflows/ci.yml/badge.svg)](https://github.com/frankwyf/forex/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/frankwyf/forex)](https://github.com/frankwyf/forex/releases)
[![MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Django market-data engineering application with validated CSV batch imports, transactional SQLite persistence, and interactive OHLC charts. Explore it offline with deterministic synthetic data.

**Version 0.2.0 · Python 3.12 / 3.13 · Django 5.2 LTS.** This is a local research and learning application under active development. See the [engineering roadmap](docs/roadmap.zh-CN.md) for the work required before production operation.

[中文](docs/README.zh-CN.md) · [日本語](docs/README.ja.md) · [Architecture and data contracts](docs/architecture.md)

## What works

- Historical imports reject missing, malformed, truncated and regressive batches.
- Recent imports validate all 12 providers before replacing data in a transaction.
- Provider or database failures preserve the previously committed dataset.
- Repeated imports collapse duplicate symbol/timestamp pairs.
- Historical and recent charts use explicit UTC date filters and JSON errors.
- Offline demo and tests require no Yahoo access or background worker.

## Quick start: macOS / Linux

Run from the repository root containing `manage.py`. For external-SSD development on macOS, follow [storage configuration](docs/macos-development.md) **before creating the environment or installing dependencies**.

~~~sh
git clone https://github.com/frankwyf/forex.git
cd forex
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# Use a new, dedicated demo database, separate from any existing market data.
export DJANGO_LOAD_ENV_FILE=0
export DJANGO_DEBUG=True
export DJANGO_DEMO_MODE=1
export DJANGO_DB_NAME="$PWD/demo.sqlite3"
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000 --noreload
~~~

Open [historical charts](http://127.0.0.1:8000/visual/history/) or [recent charts](http://127.0.0.1:8000/visual/recent/). The demo contains synthetic prices anchored in January 2024. `seed_demo` refuses to run when either market-data table already contains rows; it never clears a dataset.

## Windows PowerShell

Start in the same repository root; there is no second nested `cd forex` step.

~~~powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DJANGO_LOAD_ENV_FILE = "0"
$env:DJANGO_DEBUG = "True"
$env:DJANGO_DEMO_MODE = "1"
$env:DJANGO_DB_NAME = Join-Path (Get-Location) "demo.sqlite3"
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000 --noreload
~~~

## Verify a contribution

~~~sh
python -m pip check
python scripts/verify.py
# Optional focused run:
python scripts/verify.py --tests-only visualData
~~~

The verifier ignores local `.env` settings, creates disposable file-based SQLite databases inside the process temporary directory, runs configuration and migration checks, and blocks Python socket connections and live yfinance entry points during tests. Set `TMPDIR` to external storage on this Mac. CI verifies Linux, macOS and Windows on Python 3.12 plus Linux on Python 3.13.

## Configuration

The application reads process variables and, by default, an optional local `.env`. Process variables take precedence. `DJANGO_LOAD_ENV_FILE=0` disables that file entirely.

| Variable | Local default | Purpose |
| --- | --- | --- |
| DJANGO_DEMO_MODE | 0 | Set 1 for explicitly labeled synthetic demos |
| DJANGO_DEBUG | True | Local development only |
| DJANGO_SECRET_KEY | Development placeholder | A strong explicit key is required with DEBUG=False |
| DJANGO_ALLOWED_HOSTS | 127.0.0.1,localhost | Explicit hosts, without wildcard, are required with DEBUG=False |
| DJANGO_DB_NAME | Repository db.sqlite3 | Select a dedicated SQLite database |
| DJANGO_LOAD_ENV_FILE | 1 | Set 0 for isolated checks and demo sessions |

With DEBUG=False, HTTPS redirects and secure session/CSRF cookies are enabled. Public hosting also requires a production server, TLS and proxy configuration, backups, monitoring and a deployment review. Django runserver is for local development.

## Real data and scheduling

Live collection is an explicit operator action; see [data contracts and operator notes](docs/architecture.md). Automated tests and first-run demonstrations use synthetic data. A web import does not start APScheduler. Jobs are registered in UTC, but no worker is started by this repository. Per-process concurrency settings do not provide a lock across multiple workers.

Project code is MIT licensed; the bundled ECharts library retains its Apache license and [third-party notices](THIRD_PARTY_NOTICES.md). Provider market data is governed by the provider's terms and is not distributed with this project. There are no trading or account integration features.

## Project and maintenance

- [Contributing](CONTRIBUTING.md), [security reporting](SECURITY.md), [code of conduct](CODE_OF_CONDUCT.md)
- [Changelog](CHANGELOG.md), [release procedure](docs/releasing.md), [upgrade roadmap](docs/roadmap.zh-CN.md)
- Runtime dependency ranges remain in `requirements.txt`; `constraints.txt` records the tested dependency snapshot. Review updates through CI. Platform-specific dependencies may still be resolved by pip; this is not a hash-locked supply-chain manifest.

Source releases contain tracked code, documentation and tests as ZIP/tar.gz plus SHA-256 checksums. They exclude local environments, databases, secrets and generated market data.
