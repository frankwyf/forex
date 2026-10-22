"""Reject real network access during application tests."""

from contextlib import ExitStack
from unittest.mock import patch

from django.test.runner import DiscoverRunner


class OfflineDiscoverRunner(DiscoverRunner):
    def run_tests(self, test_labels, **kwargs):
        with ExitStack() as stack:
            for target in (
                "socket.create_connection", "socket.getaddrinfo",
                "socket.socket.connect", "socket.socket.connect_ex",
                "yfinance.Ticker", "yfinance.download",
            ):
                stack.enter_context(patch(target, side_effect=RuntimeError(
                    "Network access is disabled in tests; use a mocked provider"
                )))
            return super().run_tests(test_labels, **kwargs)
