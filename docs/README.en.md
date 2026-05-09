# Forex Local Visual (English)

Language: English | [中文](README.zh-CN.md) | [日本語](README.ja.md)

## Overview

Forex Local Visual is a Django-based open-source project for collecting and visualizing forex, commodity, and crypto data.

## Features

- Scheduled data collection with APScheduler
- SQLite-backed storage through Django ORM
- Interactive charts built with pyecharts
- Extensible app structure for processing and visualization

## Quick Start

1. Create and activate a virtual environment.

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

Set values for DJANGO_SECRET_KEY, DJANGO_DEBUG, and DJANGO_ALLOWED_HOSTS.

4. Initialize database and run server.

```powershell
python manage.py migrate
python manage.py runserver
```

Visit: http://127.0.0.1:8000/visual/

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Run checks before pushing.
4. Open a pull request with clear context.

## Security and Privacy

Do not commit .env files, local databases, log files, or generated CSV datasets.

## License

Licensed under MIT. See ../LICENSE.
