from io import StringIO
from datetime import datetime, timezone
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import DatabaseError
from django.test import TestCase, override_settings

from scheduledTask.models import HistoricalData, RecentData


@override_settings(DEMO_MODE=True)
class DemoCommandTests(TestCase):
    def test_offline_demo_populates_both_pages_and_charts(self):
        with patch("scheduledTask.DataCollector.yf.Ticker", side_effect=AssertionError("No live provider")):
            call_command("seed_demo", stdout=StringIO())
        self.assertEqual(HistoricalData.objects.values("symbol").distinct().count(), 12)
        self.assertEqual(RecentData.objects.values("symbol").distinct().count(), 12)
        for endpoint in ("get_historical_chart", "get_recent_chart"):
            response = self.client.get(f"/visual/{endpoint}/", {"symbol": "EUR/USD"})
            self.assertEqual(response.status_code, 200)
        for path in ("/visual/history/", "/visual/recent/"):
            self.assertContains(self.client.get(path), "Synthetic demo data")

    @override_settings(DEMO_MODE=False)
    def test_demo_requires_explicit_mode(self):
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.assertFalse(HistoricalData.objects.exists())
        self.assertFalse(RecentData.objects.exists())

    def test_existing_data_and_repeat_run_are_refused(self):
        call_command("seed_demo", stdout=StringIO())
        before = (HistoricalData.objects.count(), RecentData.objects.count())
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.assertEqual((HistoricalData.objects.count(), RecentData.objects.count()), before)

    def test_demo_rolls_back_if_second_table_insert_fails(self):
        with patch("scheduledTask.models.RecentData.objects.bulk_create", side_effect=DatabaseError("synthetic failure")):
            with self.assertRaises(DatabaseError):
                call_command("seed_demo", stdout=StringIO())
        self.assertEqual(HistoricalData.objects.count(), 0)
        self.assertEqual(RecentData.objects.count(), 0)

    def test_one_populated_table_is_enough_to_refuse_demo(self):
        row = RecentData.objects.create(
            symbol="EXISTING", date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            open=1, high=2, low=0.5, close=1.5,
        )
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.assertTrue(RecentData.objects.filter(pk=row.pk).exists())
        self.assertEqual(HistoricalData.objects.count(), 0)
