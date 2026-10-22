import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase


class ConfigurationTests(SimpleTestCase):
    def test_live_provider_entry_point_is_blocked_by_offline_runner(self):
        import yfinance

        with self.assertRaisesRegex(RuntimeError, "Network access is disabled"):
            yfinance.Ticker("SYNTHETIC_TEST_ONLY")

    def configured_process(self, **values):
        env = {key: value for key, value in os.environ.items() if not key.startswith("DJANGO_")}
        env.update({"DJANGO_LOAD_ENV_FILE": "0", "DJANGO_DEBUG": "False", **values})
        return subprocess.run(
            [sys.executable, "-c", "from forex import settings as s; print(s.DEBUG, s.SESSION_COOKIE_SECURE, s.CSRF_COOKIE_SECURE, s.SECURE_SSL_REDIRECT)"],
            cwd=Path(__file__).resolve().parent.parent, env=env,
            capture_output=True, text=True, check=False,
        )

    def test_production_rejects_default_or_weak_secret(self):
        for key in ("", "short", "a" * 60, "replace-with-your-secret-key" * 3):
            with self.subTest(key_length=len(key)):
                result = self.configured_process(DJANGO_SECRET_KEY=key, DJANGO_ALLOWED_HOSTS="example.invalid")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("strong DJANGO_SECRET_KEY", result.stderr)

    def test_production_requires_explicit_hosts(self):
        for hosts in ("", "*"):
            with self.subTest(hosts=hosts):
                result = self.configured_process(DJANGO_SECRET_KEY="synthetic-valid-test-only-key-0123456789-ABCDEFGHIJKLMN", DJANGO_ALLOWED_HOSTS=hosts)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("explicit DJANGO_ALLOWED_HOSTS", result.stderr)

    def test_production_enables_secure_transport_and_cookies(self):
        result = self.configured_process(
            DJANGO_SECRET_KEY="synthetic-valid-test-only-key-0123456789-ABCDEFGHIJKLMN",
            DJANGO_ALLOWED_HOSTS="example.invalid",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "False True True True")

    def test_disabled_env_loader_does_not_read_local_env(self):
        from forex import settings

        with TemporaryDirectory() as directory:
            Path(directory, ".env").write_text("FOREX_SYNTHETIC_ENV_MARKER=loaded\n", encoding="utf-8")
            with patch.object(settings, "BASE_DIR", Path(directory)), patch.dict(os.environ, {"DJANGO_LOAD_ENV_FILE": "0"}):
                with patch.object(Path, "read_text", side_effect=AssertionError("env file read")):
                    settings._load_env_file()

    def test_registered_schedule_uses_utc_without_starting_worker(self):
        from datetime import datetime, timezone
        from scheduledTask.views import scheduler

        self.assertFalse(scheduler.running)
        trigger = scheduler.get_job("collect_history_data").trigger
        self.assertEqual(str(trigger.timezone), "UTC")
        now = datetime(2026, 10, 23, 12, 14, tzinfo=timezone.utc)
        self.assertEqual(trigger.get_next_fire_time(None, now), datetime(2026, 10, 23, 12, 15, tzinfo=timezone.utc))
