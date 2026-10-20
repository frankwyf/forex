# macOS Development

The Django project root is the repository root: `manage.py`, `requirements.txt`, and `forex/settings.py` are all here. Do not change into a nested `forex/forex` directory.

## External SSD setup (zsh)

Keep the checkout on the external SSD and configure caches before installing packages. The paths below match this machine; change `DEV_STORAGE` if the SSD is mounted elsewhere.

```zsh
cd /Volumes/KIOXIA_SSD/Personal_Project/GitHub_Projects/forex
export DEV_STORAGE=/Volumes/KIOXIA_SSD/Personal_Project/GitHub_Projects/.codex-dev-storage

mkdir -p "$DEV_STORAGE"/{uv/cache,uv/python,uv/bin,uv/tools,uv/tool-bin,pip/cache,xdg/cache,xdg/data,tmp}
export UV_CACHE_DIR="$DEV_STORAGE/uv/cache"
export UV_PYTHON_INSTALL_DIR="$DEV_STORAGE/uv/python"
export UV_PYTHON_BIN_DIR="$DEV_STORAGE/uv/bin"
export UV_TOOL_DIR="$DEV_STORAGE/uv/tools"
export UV_TOOL_BIN_DIR="$DEV_STORAGE/uv/tool-bin"
export PIP_CACHE_DIR="$DEV_STORAGE/pip/cache"
export XDG_CACHE_HOME="$DEV_STORAGE/xdg/cache"
export XDG_DATA_HOME="$DEV_STORAGE/xdg/data"
export TMPDIR="$DEV_STORAGE/tmp"

python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The project currently uses pip and does not require uv. The uv paths are set so a future uv-managed install will also stay on the external SSD. The virtual environment belongs inside this checkout at `.venv`.

## Local checks and isolated database

Set `DJANGO_DB_NAME` for validation so migrations and tests do not touch the normal `db.sqlite3` file:

```zsh
export DJANGO_DB_NAME="$DEV_STORAGE/tmp/forex-mac-check.sqlite3"
python manage.py check
python manage.py migrate --noinput
python manage.py test
python manage.py runserver 127.0.0.1:8000 --noreload
```

Open <http://127.0.0.1:8000/visual/history/> to check the visualization page. An empty new database renders the page without market rows. Do not run the Yahoo Finance collection job for development checks; the reliability tests use synthetic CSVs and mocked providers.

Each historical collection writes into a new per-run batch directory. The scheduler imports only the directory returned by that collection and removes it afterward; a failed or interrupted run cannot be mixed with CSVs from another run. The importer validates every expected file, then checks inside a database transaction that the candidate retains every existing timestamp and per-symbol row count before replacing rows atomically. A truncated or gapped batch is rejected with per-symbol counts and missing timestamp ranges, while provider failures, invalid CSVs, and database errors preserve the previous dataset.

An intentional reduction is disabled in the scheduled job. After reviewing the candidate CSVs, the reported missing ranges, and a backup of the database, an operator can explicitly call `replace_historical_data_from_csv(reviewed_batch, allow_data_shrink=True)`. The importer records the approved reduction in its warning log with per-symbol counts and ranges.

## Configuration and scheduling

`forex/settings.py` reads optional values from the process environment and a repository-local `.env` file. Keep `.env` untracked and do not put real credentials in test fixtures. The checked-in `.env.example` contains placeholders only.

The project sets Django to UTC. APScheduler is configured in `scheduledTask/views.py`, but the current repository has no application startup hook or `scheduler.start()` call. Importing Django views therefore does not start a background collector. If scheduling is enabled later, configure its timezone explicitly and run it as a single, separately managed process; do not start it from each development-server worker.

## Windows

Windows PowerShell instructions remain in the main README and the existing localized README files. They use the same repository-root layout.
