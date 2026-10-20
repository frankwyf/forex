"""Validated data imports for scheduled market-data jobs."""

import math
from pathlib import Path

import pandas as pd
from django.db import transaction

from .models import HistoricalData


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


def replace_historical_data_from_csv(directory: str | Path) -> int:
    """Atomically replace historical data after validating a complete CSV batch.

    All expected provider files are parsed and validated before the existing
    table is touched. Duplicate symbol/timestamp pairs in the incoming batch
    collapse to the last row, making a repeated import idempotent.
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
        HistoricalData.objects.all().delete()
        HistoricalData.objects.bulk_create(rows)

    return len(rows)
