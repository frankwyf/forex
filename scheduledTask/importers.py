"""Validated data imports for scheduled market-data jobs."""

import logging
import math
from collections import defaultdict
from pathlib import Path

import pandas as pd
from django.db import transaction

from .models import HistoricalData, RecentData


HISTORICAL_FILE_SYMBOLS = {
    "EURUSD.csv": "EUR/USD",
    "USDJPY.csv": "USD/JPY",
    "JPYCNY.csv": "JPY/CNY",
    "USDCNY.csv": "USD/CNY",
    "AUDCNY.csv": "AUD/CNY",
    "GBPUSD.csv": "GBP/USD",
    "EURGBP.csv": "EUR/GBP",
    "EURJPY.csv": "EUR/JPY",
    "GBPJPY.csv": "GBP/JPY",
    "NZDUSD.csv": "NZD/USD",
    "gold.csv": "gold",
    "bitcoin.csv": "bitcoin",
}
REQUIRED_HISTORICAL_COLUMNS = ("Date", "Open", "High", "Low", "Close")
PRICE_COLUMNS = ("Open", "High", "Low", "Close")
logger = logging.getLogger(__name__)

RECENT_DATA_FILE_SYMBOLS = {
    "EURUSD_recent.csv": "EUR/USD",
    "USDJPY_recent.csv": "USD/JPY",
    "JPYCNY_recent.csv": "JPY/CNY",
    "USDCNY_recent.csv": "USD/CNY",
    "AUDCNY_recent.csv": "AUD/CNY",
    "GBPUSD_recent.csv": "GBP/USD",
    "EURGBP_recent.csv": "EUR/GBP",
    "EURJPY_recent.csv": "EUR/JPY",
    "GBPJPY_recent.csv": "GBP/JPY",
    "NZDUSD_recent.csv": "NZD/USD",
    "gold_recent.csv": "gold",
    "bitcoin_recent.csv": "bitcoin",
}
REQUIRED_RECENT_COLUMNS = ("Datetime", "Open", "High", "Low", "Close")


def _validated_rows(csv_path: Path, symbol: str) -> list[HistoricalData]:
    frame = pd.read_csv(csv_path, encoding="utf-8-sig")
    missing_columns = [column for column in REQUIRED_HISTORICAL_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"{csv_path.name} is missing required columns: {', '.join(missing_columns)}")
    if frame.empty:
        raise ValueError(f"{csv_path.name} contains no market data")

    timestamps = pd.to_datetime(frame["Date"], errors="coerce", utc=True)
    if timestamps.isna().any():
        invalid_rows = (timestamps.index[timestamps.isna()] + 2).tolist()
        raise ValueError(f"{csv_path.name} contains invalid timestamps on CSV rows: {invalid_rows}")

    prices = {}
    for column in PRICE_COLUMNS:
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.isna().any():
            invalid_rows = (values.index[values.isna()] + 2).tolist()
            raise ValueError(f"{csv_path.name} contains invalid {column} values on CSV rows: {invalid_rows}")
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError(f"{csv_path.name} contains non-finite {column} values")
        prices[column] = values

    return [
        HistoricalData(
            symbol=symbol,
            date=timestamp.to_pydatetime(),
            open=float(prices["Open"].iloc[index]),
            high=float(prices["High"].iloc[index]),
            low=float(prices["Low"].iloc[index]),
            close=float(prices["Close"].iloc[index]),
        )
        for index, timestamp in enumerate(timestamps)
    ]


def _coverage_regressions(rows: list[HistoricalData]) -> dict[str, tuple[int, int, set]]:
    """Return timestamp or row-count reductions for any stored symbol."""
    candidate_dates = defaultdict(set)
    candidate_counts = defaultdict(int)
    for row in rows:
        candidate_dates[row.symbol].add(row.date)
        candidate_counts[row.symbol] += 1

    existing_dates = defaultdict(set)
    existing_counts = defaultdict(int)
    for symbol, timestamp in HistoricalData.objects.values_list("symbol", "date"):
        existing_dates[symbol].add(timestamp)
        existing_counts[symbol] += 1

    regressions = {}
    for symbol, timestamps in existing_dates.items():
        candidate_timestamps = candidate_dates.get(symbol, set())
        missing = timestamps - candidate_timestamps
        if missing or candidate_counts[symbol] < existing_counts[symbol]:
            regressions[symbol] = (existing_counts[symbol], candidate_counts[symbol], missing)
    return regressions


def _format_missing_timestamps(regressions: dict[str, tuple[int, int, set]]) -> str:
    return "; ".join(
        f"{symbol}: {existing_count} existing rows, {candidate_count} candidate rows"
        + (
            f", {len(missing)} existing timestamps missing "
            f"({min(missing).isoformat()} through {max(missing).isoformat()})"
            if missing
            else ""
        )
        for symbol, (existing_count, candidate_count, missing) in sorted(regressions.items())
    )


def replace_historical_data_from_csv(
    directory: str | Path, *, allow_data_shrink: bool = False
) -> int:
    """Atomically replace history after validating the batch and preserving prior coverage.

    All expected provider files are parsed and validated before the existing
    table is touched. Duplicate symbol/timestamp pairs in the incoming batch
    collapse to the last row, making a repeated import idempotent. Every
    existing stored timestamp and per-symbol row count must remain in the new
    batch. An intentional reduction requires the explicit
    ``allow_data_shrink=True`` override after reviewing the reported symbols
    and timestamp ranges.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"Historical data directory does not exist: {directory}")

    rows_by_key = {}
    for filename, symbol in HISTORICAL_FILE_SYMBOLS.items():
        csv_path = directory / filename
        if not csv_path.is_file():
            raise FileNotFoundError(f"Historical data batch is incomplete; missing {filename}")
        for row in _validated_rows(csv_path, symbol):
            rows_by_key[(row.symbol, row.date)] = row

    rows = list(rows_by_key.values())
    if not rows:
        raise ValueError("Historical data batch contains no rows")

    with transaction.atomic():
        regressions = _coverage_regressions(rows)
        if regressions and not allow_data_shrink:
            raise ValueError(
                "Historical batch would regress existing historical coverage: "
                f"{_format_missing_timestamps(regressions)}. Review the candidate data before "
                "using allow_data_shrink=True for an intentional reduction."
            )

        HistoricalData.objects.all().delete()
        HistoricalData.objects.bulk_create(rows)

    if regressions:
        logger.warning(
            "Applied explicitly authorized historical data shrink: %s",
            _format_missing_timestamps(regressions),
        )

    return len(rows)


def _validated_recent_rows(csv_path: Path, symbol: str) -> list[RecentData]:
    frame = pd.read_csv(csv_path, encoding="utf-8-sig")
    missing_columns = [column for column in REQUIRED_RECENT_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"{csv_path.name} is missing required columns: {', '.join(missing_columns)}")
    if frame.empty:
        raise ValueError(f"{csv_path.name} contains no recent market data")

    timestamps = pd.to_datetime(frame["Datetime"], format="mixed", errors="coerce", utc=True)
    if timestamps.isna().any():
        invalid_rows = (timestamps.index[timestamps.isna()] + 2).tolist()
        raise ValueError(f"{csv_path.name} contains invalid timestamps on CSV rows: {invalid_rows}")

    prices = {}
    for column in PRICE_COLUMNS:
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.isna().any():
            invalid_rows = (values.index[values.isna()] + 2).tolist()
            raise ValueError(f"{csv_path.name} contains invalid {column} values on CSV rows: {invalid_rows}")
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError(f"{csv_path.name} contains non-finite {column} values")
        prices[column] = values

    rows_by_timestamp = {}
    for index, timestamp in enumerate(timestamps):
        market_timestamp = timestamp.to_pydatetime()
        rows_by_timestamp[market_timestamp] = RecentData(
            symbol=symbol,
            date=market_timestamp,
            open=float(prices["Open"].iloc[index]),
            high=float(prices["High"].iloc[index]),
            low=float(prices["Low"].iloc[index]),
            close=float(prices["Close"].iloc[index]),
        )
    return list(rows_by_timestamp.values())


def replace_recent_data_from_csv(directory: str | Path) -> int:
    """Replace recent market rows only after validating a complete provider batch.

    Repeated timestamps within a provider file collapse to the last row. The
    existing dataset is replaced atomically after every expected file and row
    has passed validation.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"Recent data batch directory does not exist: {directory}")

    expected_files = set(RECENT_DATA_FILE_SYMBOLS)
    actual_files = {
        path.name
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() == ".csv"
    }
    missing_files = sorted(expected_files - actual_files)
    unexpected_files = sorted(actual_files - expected_files)
    if missing_files or unexpected_files:
        details = []
        if missing_files:
            details.append(f"missing files: {', '.join(missing_files)}")
        if unexpected_files:
            details.append(f"unexpected files: {', '.join(unexpected_files)}")
        raise ValueError("Recent data batch is incomplete (" + "; ".join(details) + ")")

    rows_by_key = {}
    for filename, symbol in RECENT_DATA_FILE_SYMBOLS.items():
        for row in _validated_recent_rows(directory / filename, symbol):
            rows_by_key[(row.symbol, row.date)] = row

    rows = list(rows_by_key.values())
    if not rows:
        raise ValueError("Recent data batch contains no rows")

    with transaction.atomic():
        RecentData.objects.all().delete()
        RecentData.objects.bulk_create(rows)

    return len(rows)
