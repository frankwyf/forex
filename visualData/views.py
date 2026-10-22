"""Read-only pages and validated ECharts JSON endpoints."""

from datetime import datetime, time, timedelta, timezone
import json

from django.db.models import Max, Min
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from pyecharts import options as opts
from pyecharts.charts import Line

from scheduledTask.models import HistoricalData, RecentData
from .forms import HistoricalChartQuery, RecentChartQuery


def _data_page(request, model, template):
    symbols = list(model.objects.order_by("symbol").values_list("symbol", flat=True).distinct())
    default_symbol = "USD/JPY" if "USD/JPY" in symbols else symbols[0] if symbols else None
    date_range = model.objects.aggregate(min_date=Min("date"), max_date=Max("date"))
    return render(request, template, {
        "symbols": symbols, "default_symbol": default_symbol, "date_range": date_range,
        "demo_mode": settings.DEMO_MODE,
    })


def history_data(request):
    return _data_page(request, HistoricalData, "history_data.html")


def recent_data(request):
    return _data_page(request, RecentData, "recent_data.html")


def _invalid_query(form):
    return JsonResponse({
        "error": "Invalid chart parameters.",
        "fields": form.errors.get_json_data(),
    }, status=400)


def _chart_response(data, title, date_format):
    rows = list(data)
    line = Line().add_xaxis([row.date.strftime(date_format) for row in rows])
    for label, field in (("Open", "open"), ("High", "high"), ("Low", "low"), ("Close", "close")):
        line.add_yaxis(
            label, [getattr(row, field) for row in rows],
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False),
        )
    line.set_global_opts(
        title_opts=opts.TitleOpts(title=title),
        datazoom_opts=[opts.DataZoomOpts()],
        yaxis_opts=opts.AxisOpts(
            type_="value", is_scale=True,
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
    )
    return JsonResponse(json.loads(line.dump_options_with_quotes()))


@require_GET
def get_historical_chart(request):
    form = HistoricalChartQuery(request.GET)
    if not form.is_valid():
        return _invalid_query(form)
    query = form.cleaned_data
    data = HistoricalData.objects.filter(symbol=query["symbol"])
    if not data.exists():
        return JsonResponse({"error": "No data for this symbol."}, status=404)
    if query["start_date"]:
        start = datetime.combine(query["start_date"], time.min, tzinfo=timezone.utc)
        data = data.filter(date__gte=start)
    if query["end_date"]:
        # Inclusive UTC calendar day, including intraday records at 23:59.
        end = datetime.combine(query["end_date"], time.max, tzinfo=timezone.utc)
        data = data.filter(date__lte=end)
    return _chart_response(data.order_by("date"), "Historical Data", "%Y-%m-%d")


@require_GET
def get_recent_chart(request):
    form = RecentChartQuery(request.GET)
    if not form.is_valid():
        return _invalid_query(form)
    query = form.cleaned_data
    data = RecentData.objects.filter(symbol=query["symbol"])
    end = data.aggregate(max_date=Max("date"))["max_date"]
    if end is None:
        return JsonResponse({"error": "No data for this symbol."}, status=404)
    days = {"1d": 1, "3d": 3, "1w": 7, "1m": 30}[query["time_range"]]
    data = data.filter(date__gte=end - timedelta(days=days), date__lte=end)
    return _chart_response(data.order_by("date"), "Recent Data", "%Y-%m-%d %H:%M")
