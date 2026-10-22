# macOS Development

The Django project root is the repository root: `manage.py`, `requirements.txt`, and `forex/settings.py` are all here. Do not change into a nested `forex/forex` directory.

## External SSD setup (zsh)

Keep the checkout on the external SSD and configure caches before installing packages. The paths below match this machine; change `DEV_STORAGE` if the SSD is mounted elsewhere.

```zsh
cd /Volumes/KIOXIA_SSD/Personal_Project/GitHub_Projects/forex
export DEV_STORAGE=/Volumes/KIOXIA_SSD/Personal_Project/GitHub_Projects/.codex-dev-storage

mkdir -p "$DEV_STORAGE"/{uv/cache,uv/python,uv/bin,uv/tools,uv/tool-bin,pip/cache,xdg/cache,xdg/data,tmp,hf,torch,mpl,playwright}
export UV_CACHE_DIR="$DEV_STORAGE/uv/cache"
export UV_PYTHON_INSTALL_DIR="$DEV_STORAGE/uv/python"
export UV_PYTHON_BIN_DIR="$DEV_STORAGE/uv/bin"
export UV_TOOL_DIR="$DEV_STORAGE/uv/tools"
export UV_TOOL_BIN_DIR="$DEV_STORAGE/uv/tool-bin"
export PIP_CACHE_DIR="$DEV_STORAGE/pip/cache"
export XDG_CACHE_HOME="$DEV_STORAGE/xdg/cache"
export XDG_DATA_HOME="$DEV_STORAGE/xdg/data"
export TMPDIR="$DEV_STORAGE/tmp"
export HF_HOME="$DEV_STORAGE/hf"
export TORCH_HOME="$DEV_STORAGE/torch"
export MPLCONFIGDIR="$DEV_STORAGE/mpl"
export PLAYWRIGHT_BROWSERS_PATH="$DEV_STORAGE/playwright"

python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Before running the setup, use `pwd -P`, `diskutil info /Volumes/KIOXIA_SSD` and `df -h / /Volumes/KIOXIA_SSD` to verify the physical repository path, USB/external device location, mount point and capacity. Do not infer device location from a directory name or fall back to internal storage if the SSD is absent. Reuse an existing repository `.venv` when present.

The project uses pip with `requirements.txt` and a reviewed `constraints.txt` snapshot. It does not require uv. All exported cache and temporary paths must be present in the same process that installs or tests. Existing macOS applications may still write small system caches.

## Local checks and isolated database

Run the isolated verifier first. It ignores `.env` and normal database settings and creates disposable file-based SQLite databases under the external `TMPDIR`:

```zsh
python -m pip check
python scripts/verify.py
```

For an offline browser demonstration, choose a new dedicated database path, then migrate only that new database:

```zsh
export DJANGO_LOAD_ENV_FILE=0
export DJANGO_DEBUG=True
export DJANGO_DEMO_MODE=1
export DJANGO_DB_NAME="$DEV_STORAGE/tmp/forex-demo-v020.sqlite3"
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000 --noreload
```

Open <http://127.0.0.1:8000/visual/history/> to check the visualization page. Demo values are synthetic; the command refuses databases containing market rows. Do not run Yahoo Finance collection for development checks.

Each historical collection writes into a new per-run batch directory. The scheduler imports only the directory returned by that collection and removes it afterward; a failed or interrupted run cannot be mixed with CSVs from another run. The importer validates every expected file, then checks inside a database transaction that the candidate retains every existing timestamp and per-symbol row count before replacing rows atomically. A truncated or gapped batch is rejected with per-symbol counts and missing timestamp ranges, while provider failures, invalid CSVs, and database errors preserve the previous dataset.

An intentional reduction is disabled in the scheduled job. After reviewing the candidate CSVs, the reported missing ranges, and a backup of the database, an operator can explicitly call `replace_historical_data_from_csv(reviewed_batch, allow_data_shrink=True)`. The importer records the approved reduction in its warning log with per-symbol counts and ranges.

## Configuration and scheduling

`forex/settings.py` reads optional values from the process environment and a repository-local `.env` file. Keep `.env` untracked and do not put real credentials in test fixtures. The checked-in `.env.example` contains placeholders only.

The project sets Django and APScheduler Cron triggers explicitly to UTC. The repository has no application startup hook or `scheduler.start()` call. Importing Django views does not start a collector. If scheduling is enabled later, run it as a single, separately managed process with cross-process locking; per-process instance limits do not protect multiple workers.

## Windows

Windows PowerShell instructions remain in the main README and the existing localized README files. They use the same repository-root layout.
