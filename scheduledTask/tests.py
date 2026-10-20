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

    def write_batch(
        self,
        open_price=1.25,
        *,
        dates=None,
        missing_column=None,
        invalid_timestamp=False,
        duplicate=False,
    ):
        if dates is None:
            dates = ["2024-01-02"]
        for filename in HISTORICAL_FILE_SYMBOLS:
            rows = [
                {
                    "Date": "not-a-date" if invalid_timestamp and filename == "EURUSD.csv" else market_date,
                    "Open": open_price,
                    "High": open_price + 0.1,
                    "Low": open_price - 0.1,
                    "Close": open_price + 0.05,
                }
                for market_date in dates
            ]
            if duplicate and filename == "EURUSD.csv":
                row = rows[0]
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

    def test_valid_batch_updates_existing_rows_and_keeps_frontend_query_compatible(self):
        HistoricalData.objects.create(
            symbol="EUR/USD",
            date=datetime(2024, 1, 2, tzinfo=timezone.utc),
            open=9,
            high=10,
            low=8,
            close=9.5,
        )
        self.write_batch()

        imported = replace_historical_data_from_csv(self.data_dir)

        self.assertEqual(imported, len(HISTORICAL_FILE_SYMBOLS))
        self.assertFalse(HistoricalData.objects.filter(symbol="OLD/PAIR").exists())
        self.assertEqual(HistoricalData.objects.get(symbol="EUR/USD").open, 1.25)

        response = self.client.get("/visual/get_historical_chart/?symbol=EUR/USD")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_nonempty_but_truncated_batch_preserves_previous_dataset(self):
        self.write_batch(dates=["2024-01-01", "2024-01-02", "2024-01-03"])
        replace_historical_data_from_csv(self.data_dir)
        previous_rows = list(
            HistoricalData.objects.filter(symbol="EUR/USD").order_by("date").values_list("date", "close")
        )

        self.write_batch(dates=["2024-01-02", "2024-01-03"])
        with self.assertRaisesRegex(ValueError, "regress existing historical coverage"):
            replace_historical_data_from_csv(self.data_dir)

        current_rows = list(
            HistoricalData.objects.filter(symbol="EUR/USD").order_by("date").values_list("date", "close")
        )
        self.assertEqual(current_rows, previous_rows)

    def test_same_count_batch_that_omits_existing_timestamp_is_rejected(self):
        self.write_batch(dates=["2024-01-01", "2024-01-02", "2024-01-03"])
        replace_historical_data_from_csv(self.data_dir)
        previous_rows = list(
            HistoricalData.objects.filter(symbol="EUR/USD").order_by("date").values_list("date", "close")
        )

        self.write_batch(dates=["2024-01-01", "2024-01-03", "2024-01-04"])
        with self.assertRaisesRegex(ValueError, "regress existing historical coverage"):
            replace_historical_data_from_csv(self.data_dir)

        current_rows = list(
            HistoricalData.objects.filter(symbol="EUR/USD").order_by("date").values_list("date", "close")
        )
        self.assertEqual(current_rows, previous_rows)

    def test_row_count_regression_is_rejected_even_when_timestamp_remains(self):
        self.write_batch()
        replace_historical_data_from_csv(self.data_dir)
        previous = HistoricalData.objects.get(symbol="EUR/USD")
        HistoricalData.objects.create(
            symbol=previous.symbol,
            date=previous.date,
            open=previous.open,
            high=previous.high,
            low=previous.low,
            close=previous.close,
        )
        self.write_batch()

        with self.assertRaisesRegex(ValueError, "existing rows"):
            replace_historical_data_from_csv(self.data_dir)

        self.assertEqual(HistoricalData.objects.filter(symbol="EUR/USD").count(), 2)

    def test_intentional_data_shrink_requires_and_records_explicit_override(self):
        self.write_batch(dates=["2024-01-01", "2024-01-02", "2024-01-03"])
        replace_historical_data_from_csv(self.data_dir)
        self.write_batch(dates=["2024-01-02", "2024-01-03"])

        with self.assertLogs("scheduledTask.importers", level="WARNING") as captured:
            imported = replace_historical_data_from_csv(self.data_dir, allow_data_shrink=True)

        self.assertEqual(imported, len(HISTORICAL_FILE_SYMBOLS) * 2)
        self.assertIn("Applied explicitly authorized historical data shrink", captured.output[0])
        self.assertEqual(HistoricalData.objects.filter(symbol="EUR/USD").count(), 2)

    def test_partial_provider_failure_preserves_previous_dataset(self):
        previous = self.seed_previous_dataset()

        with patch("scheduledTask.views.collectHistoryData", return_value=False):
            from scheduledTask.views import collect_history_data

            collect_history_data()

        self.assertEqual(list(HistoricalData.objects.values_list("pk", "symbol")), [(previous.pk, "OLD/PAIR")])

    def test_scheduler_imports_and_cleans_only_the_returned_batch(self):
        from scheduledTask.views import collect_history_data

        batch_directory = self.data_dir / ".batch-current-run"
        batch_directory.mkdir()
        with (
            patch("scheduledTask.views.collectHistoryData", return_value=batch_directory),
            patch("scheduledTask.views.replace_historical_data_from_csv", return_value=12) as importer,
        ):
            imported = collect_history_data()

        self.assertEqual(imported, 12)
        importer.assert_called_once_with(batch_directory)
        self.assertFalse(batch_directory.exists())

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
        self.assertEqual(list(self.data_dir.glob(".batch-*")), [])

    def test_successful_collections_write_to_separate_batch_directories(self):
        from scheduledTask.DataCollector import collectHistoryData

        stale_file = self.data_dir / "EURUSD.csv"
        stale_file.write_text("stale data", encoding="utf-8")

        class ValidTicker:
            def history(self, **kwargs):
                return pd.DataFrame(
                    {"Open": [1.0], "High": [1.1], "Low": [0.9], "Close": [1.05]},
                    index=pd.DatetimeIndex(["2024-01-02"], name="Date"),
                )

        with patch("scheduledTask.DataCollector.yf.Ticker", return_value=ValidTicker()):
            first_batch = collectHistoryData(self.data_dir)
            second_batch = collectHistoryData(self.data_dir)

        self.assertNotEqual(first_batch, second_batch)
        self.assertEqual(set(path.name for path in first_batch.iterdir()), set(HISTORICAL_FILE_SYMBOLS))
        self.assertEqual(set(path.name for path in second_batch.iterdir()), set(HISTORICAL_FILE_SYMBOLS))
        self.assertEqual(stale_file.read_text(encoding="utf-8"), "stale data")

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
                replace_historical_data_from_csv(self.data_dir, allow_data_shrink=True)

        self.assertTrue(HistoricalData.objects.filter(pk=previous.pk).exists())

    def test_repeated_and_overlapping_batches_are_idempotent(self):
        self.write_batch(open_price=1.25, dates=["2024-01-02"], duplicate=True)
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
        self.write_batch(open_price=2.5, dates=["2024-01-01", "2024-01-02", "2024-01-03"])
        replace_historical_data_from_csv(self.data_dir)

        rows = HistoricalData.objects.filter(symbol="EUR/USD")
        self.assertEqual(rows.count(), 3)
        self.assertEqual(rows.order_by("date").first().open, 2.5)
        self.assertTrue(HistoricalData.objects.filter(symbol="EUR/USD", date__date="2024-01-01").exists())
