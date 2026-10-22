from datetime import datetime, timezone

from django.test import TestCase

from scheduledTask.models import HistoricalData, RecentData


class ChartContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for model in (HistoricalData, RecentData):
            for day, hour in ((2, 0), (2, 23), (3, 0)):
                model.objects.create(
                    symbol="EUR/USD", date=datetime(2024, 1, day, hour, tzinfo=timezone.utc),
                    open=1.1, high=1.3, low=1, close=1.2,
                )

    def test_pages_render_with_empty_database(self):
        HistoricalData.objects.all().delete()
        RecentData.objects.all().delete()
        for path in ("/visual/history/", "/visual/recent/"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_missing_symbol_returns_json_400(self):
        for endpoint in ("get_historical_chart", "get_recent_chart"):
            with self.subTest(endpoint=endpoint):
                response = self.client.get(f"/visual/{endpoint}/")
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.json())

    def test_unknown_symbol_returns_json_404(self):
        for endpoint in ("get_historical_chart", "get_recent_chart"):
            with self.subTest(endpoint=endpoint):
                response = self.client.get(f"/visual/{endpoint}/", {"symbol": "NO/DATA"})
                self.assertEqual(response.status_code, 404)
                self.assertIn("error", response.json())

    def test_invalid_dates_and_reversed_range_return_400(self):
        for params in (
            {"start_date": "not-a-date"}, {"end_date": "2024-02-30"},
            {"start_date": "2024-01-03", "end_date": "2024-01-02"},
        ):
            with self.subTest(params=params):
                response = self.client.get("/visual/get_historical_chart/", {"symbol": "EUR/USD", **params})
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.json())

    def test_end_date_includes_entire_utc_day(self):
        response = self.client.get("/visual/get_historical_chart/", {
            "symbol": "EUR/USD", "end_date": "2024-01-02",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(len(response.json()["series"][0]["data"]), 2)

    def test_open_start_range_filters_without_end_date(self):
        response = self.client.get("/visual/get_historical_chart/", {
            "symbol": "EUR/USD", "start_date": "2024-01-03",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["series"][0]["data"]), 1)

    def test_empty_valid_range_returns_empty_chart(self):
        response = self.client.get("/visual/get_historical_chart/", {
            "symbol": "EUR/USD", "start_date": "2025-01-01",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["series"][0]["data"], [])

    def test_recent_default_and_supported_ranges_return_chart_objects(self):
        for time_range in (None, "1d", "3d", "1w", "1m"):
            params = {"symbol": "EUR/USD"}
            if time_range is not None:
                params["time_range"] = time_range
            with self.subTest(time_range=time_range):
                response = self.client.get("/visual/get_recent_chart/", params)
                self.assertEqual(response.status_code, 200)
                self.assertIsInstance(response.json(), dict)
                self.assertEqual(len(response.json()["series"]), 4)

    def test_unsupported_recent_range_returns_400(self):
        response = self.client.get("/visual/get_recent_chart/", {"symbol": "EUR/USD", "time_range": "wrong"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_chart_endpoints_are_read_only(self):
        for endpoint in ("get_historical_chart", "get_recent_chart"):
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.client.post(f"/visual/{endpoint}/").status_code, 405)
