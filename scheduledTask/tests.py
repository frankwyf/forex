from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd
from django.db import DatabaseError
from django.test import TestCase

from scheduledTask.importers import HISTORICAL_FILE_SYMBOLS, replace_historical_data_from_csv
from scheduledTask.models import HistoricalData


class HistoricalImportTests(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_batch(self, open_price=1.25, *, missing_column=None, invalid_timestamp=False, duplicate=False):
        for filename in HISTORICAL_FILE_SYMBOLS:
            row = {
                "Date": "not-a-date" if invalid_timestamp and filename == "EURUSD.csv" else "2024-01-02",
                "Open": open_price,
                "High": open_price + 0.1,
                "Low": open_price - 0.1,
                "Close": open_price + 0.05,
            }
            rows = [row]
            if duplicate and filename == "EURUSD.csv":
                rows.append(
                    {
                        **row,
                        "Open": open_price + 1,
                        "High": open_price + 1.1,
                        "Low": open_price + 0.9,
                        "Close": open_price + 1.05,
                    }
                )

            frame = pd.DataFrame(rows)
            if missing_column and filename == "EURUSD.csv":
                frame = frame.drop(columns=[missing_column])
            frame.to_csv(self.data_dir / filename, index=False)

    def seed_previous_dataset(self):
        return HistoricalData.objects.create(
            symbol="OLD/PAIR",
            date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            open=9,
            high=10,
            low=8,
            close=9.5,
        )

    def test_valid_batch_replaces_dataset_and_keeps_frontend_query_compatible(self):
        self.seed_previous_dataset()
        self.write_batch()

        imported = replace_historical_data_from_csv(self.data_dir)

        self.assertEqual(imported, len(HISTORICAL_FILE_SYMBOLS))
        self.assertFalse(HistoricalData.objects.filter(symbol="OLD/PAIR").exists())
        self.assertEqual(HistoricalData.objects.get(symbol="EUR/USD").open, 1.25)

        response = self.client.get("/visual/get_historical_chart/?symbol=EUR/USD")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_partial_provider_failure_preserves_previous_dataset(self):
        previous = self.seed_previous_dataset()

        with patch("scheduledTask.views.collectHistoryData", return_value=False):
            from scheduledTask.views import collect_history_data

            collect_history_data()

        self.assertEqual(list(HistoricalData.objects.values_list("pk", "symbol")), [(previous.pk, "OLD/PAIR")])

    def test_importing_scheduler_module_does_not_start_scheduler(self):
        from scheduledTask.views import scheduler

        self.assertFalse(scheduler.running)

    def test_collector_reports_partial_provider_failure_without_using_stale_csv(self):
        from scheduledTask.DataCollector import collectHistoryData

        stale_file = self.data_dir / "JPYCNY.csv"
        stale_file.write_text("not a valid fresh provider response", encoding="utf-8")

        def ticker_factory(ticker):
            if ticker == "JPYCNY=X":
                class FailedTicker:
                    def history(self, **kwargs):
                        raise RuntimeError("simulated provider failure")

                return FailedTicker()

            class ValidTicker:
                def history(self, **kwargs):
                    return pd.DataFrame(
                        {"Open": [1.0], "High": [1.1], "Low": [0.9], "Close": [1.05]},
                        index=pd.DatetimeIndex(["2024-01-02"], name="Date"),
                    )

            return ValidTicker()

        with patch("scheduledTask.DataCollector.yf.Ticker", side_effect=ticker_factory):
            complete = collectHistoryData(self.data_dir)

        self.assertFalse(complete)
        self.assertEqual(stale_file.read_text(encoding="utf-8"), "not a valid fresh provider response")

    def test_missing_required_column_preserves_previous_dataset(self):
        previous = self.seed_previous_dataset()
        self.write_batch(missing_column="Low")

        with self.assertRaises(ValueError):
            replace_historical_data_from_csv(self.data_dir)

        self.assertTrue(HistoricalData.objects.filter(pk=previous.pk).exists())

    def test_invalid_timestamp_preserves_previous_dataset(self):
        previous = self.seed_previous_dataset()
        self.write_batch(invalid_timestamp=True)

        with self.assertRaises(ValueError):
            replace_historical_data_from_csv(self.data_dir)

        self.assertTrue(HistoricalData.objects.filter(pk=previous.pk).exists())

    def test_missing_provider_file_preserves_previous_dataset(self):
        previous = self.seed_previous_dataset()
        self.write_batch()
        (self.data_dir / "bitcoin.csv").unlink()

        with self.assertRaises(FileNotFoundError):
            replace_historical_data_from_csv(self.data_dir)

        self.assertTrue(HistoricalData.objects.filter(pk=previous.pk).exists())

    def test_database_error_during_bulk_insert_rolls_back_delete(self):
        previous = self.seed_previous_dataset()
        self.write_batch()

        with patch(
            "scheduledTask.importers.HistoricalData.objects.bulk_create",
            side_effect=DatabaseError("simulated insert failure"),
        ):
            with self.assertRaises(DatabaseError):
                replace_historical_data_from_csv(self.data_dir)

        self.assertTrue(HistoricalData.objects.filter(pk=previous.pk).exists())

    def test_repeated_and_overlapping_batches_are_idempotent(self):
        self.write_batch(open_price=1.25, duplicate=True)
        replace_historical_data_from_csv(self.data_dir)
        replace_historical_data_from_csv(self.data_dir)

        rows = HistoricalData.objects.filter(symbol="EUR/USD")
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows.get().open, 2.25)

        HistoricalData.objects.create(
            symbol="EUR/USD",
            date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            open=0.9,
            high=1.0,
            low=0.8,
            close=0.95,
        )
        self.write_batch(open_price=2.5)
        replace_historical_data_from_csv(self.data_dir)

        rows = HistoricalData.objects.filter(symbol="EUR/USD")
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows.get().open, 2.5)
        self.assertFalse(HistoricalData.objects.filter(symbol="EUR/USD", date__date="2024-01-01").exists())
