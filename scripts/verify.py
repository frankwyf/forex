"""Run checks and offline tests against disposable, file-based SQLite databases."""

import argparse
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("labels", nargs="*", help="Optional Django test labels")
    parser.add_argument("--tests-only", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    with TemporaryDirectory(prefix="forex-verify-") as directory:
        env = os.environ.copy()
        env.update({
            "DJANGO_SETTINGS_MODULE": "forex.test_settings",
            "DJANGO_LOAD_ENV_FILE": "0",
            "DJANGO_DEBUG": "True",
            "DJANGO_DEMO_MODE": "0",
            "DJANGO_ALLOWED_HOSTS": "testserver,localhost,127.0.0.1",
            "DJANGO_SECRET_KEY": "synthetic-test-key-never-used-for-serving",
            "FOREX_VERIFY_DIR": directory,
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        commands = [] if args.tests_only else [
            ["check"], ["makemigrations", "--check", "--dry-run"],
        ]
        commands.append(["test", *args.labels, "--verbosity", "2", "--noinput"])
        for arguments in commands:
            print("Running manage.py " + " ".join(arguments), flush=True)
            result = subprocess.run(
                [sys.executable, "manage.py", *arguments], cwd=root, env=env,
                check=False,
            )
            if result.returncode:
                return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
