"""Isolated settings used by scripts/verify.py; never load a local .env."""

import os
from pathlib import Path

os.environ["DJANGO_LOAD_ENV_FILE"] = "0"

from .settings import *  # noqa: F403,E402

if not os.environ.get("FOREX_VERIFY_DIR"):
    raise RuntimeError("Use python scripts/verify.py to create an isolated test directory")

_verify_dir = Path(os.environ["FOREX_VERIFY_DIR"]).resolve()
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(_verify_dir / "checks.sqlite3"),
        "TEST": {"NAME": str(_verify_dir / "tests.sqlite3")},
    }
}
TEST_RUNNER = "forex.test_runner.OfflineDiscoverRunner"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
