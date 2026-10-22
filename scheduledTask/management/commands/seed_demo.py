"""Create deterministic synthetic market data in an empty database."""

from datetime import datetime, timedelta, timezone
import math

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction

from scheduledTask.importers import HISTORICAL_FILE_SYMBOLS
from scheduledTask.models import HistoricalData, RecentData


class Command(BaseCommand):
    help = "Seed synthetic demo rows. Refuses any database with existing market data."

    def handle(self, *args, **options):
        if not settings.DEMO_MODE:
            raise CommandError("Set DJANGO_DEMO_MODE=1 and select a new dedicated database before seeding synthetic data.")
        anchor = datetime(2024, 1, 1, tzinfo=timezone.utc)
        symbols = list(HISTORICAL_FILE_SYMBOLS.values())
        historical, recent = [], []
        for index, symbol in enumerate(symbols):
            for model, destination, count, step in (
                (HistoricalData, historical, 90, timedelta(days=1)),
                (RecentData, recent, 96, timedelta(minutes=30)),
            ):
                for offset in range(count):
                    price = 1 + index + offset * 0.01 + math.sin(offset / 5) * 0.02
                    destination.append(model(
                        symbol=symbol, date=anchor + offset * step,
                        open=price, high=price + 0.05,
                        low=price - 0.05, close=price + 0.01,
                    ))
        with transaction.atomic():
            if HistoricalData.objects.exists() or RecentData.objects.exists():
                raise CommandError(
                    "Refusing to mix demo rows with existing market data. Use a new, dedicated demo database."
                )
            HistoricalData.objects.bulk_create(historical)
            RecentData.objects.bulk_create(recent)
        self.stdout.write(self.style.SUCCESS(
            f"SYNTHETIC DEMO ONLY: {len(historical)} historical and {len(recent)} recent rows. "
            "These are not observed market prices."
        ))
