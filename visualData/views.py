import logging
from django.shortcuts import render
from scheduledTask.models import HistoricalData, RecentData
from pyecharts.charts import Line
from pyecharts import options as opts
from django.http import JsonResponse
from django.db.models import Min, Max
from datetime import timedelta

logger = logging.getLogger('visualData')

def history_data(request):
    symbols = list(HistoricalData.objects.values_list('symbol', flat=True).distinct())
    default_symbol = 'USD/JPY' if 'USD/JPY' in symbols else symbols[0] if symbols else None
    date_range = HistoricalData.objects.aggregate(min_date=Min('date'), max_date=Max('date'))
    return render(request, 'history_data.html', {'symbols': symbols, 'default_symbol': default_symbol, 'date_range': date_range})

def recent_data(request):
    symbols = list(RecentData.objects.values_list('symbol', flat=True).distinct())
    default_symbol = 'USD/JPY' if 'USD/JPY' in symbols else symbols[0] if symbols else None
    date_range = RecentData.objects.aggregate(min_date=Min('date'), max_date=Max('date'))
    return render(request, 'recent_data.html', {'symbols': symbols, 'default_symbol': default_symbol, 'date_range': date_range})


def get_historical_chart(request):
    symbol = request.GET.get('symbol')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # if start_date and end_date are not provided, use the entire data
    if not start_date and not end_date:
        try:
            data = HistoricalData.objects.filter(symbol=symbol).order_by('date')
            logger.info(f"Get historical data for {symbol} of period: all")
        except Exception as e:
            logger.error(f"Error getting historical data of {symbol}: {e}")
    else:
        if not start_date:
            # use 2020-01-01 as the default start date, format: YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]
            start_date = '2020-01-01 00:00:00'  
        elif not end_date:
            # use the latest date in the database as the default end date
            end_date = HistoricalData.objects.filter(symbol=symbol).aggregate(max_date=Max('date'))['max_date']
        
        try:
            data = HistoricalData.objects.filter(symbol=symbol, date__range=[start_date, end_date]).order_by('date')
            logger.info(f"Get historical data for {symbol} of period: {start_date} to {end_date}")
        except Exception as e:
            logger.error(f"Error getting historical data of {symbol} from {start_date} to {end_date}: {e}")
    
    try:
        dates = [d.date.strftime('%Y-%m-%d') for d in data]  # 确保日期格式正确
        opens = [d.open for d in data]
        highs = [d.high for d in data]
        lows = [d.low for d in data]
        closes = [d.close for d in data]

        line = (
            Line()
            .add_xaxis(dates)
            .add_xaxis(dates)
            .add_yaxis("Open", opens, linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("High", highs, linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("Low", lows, linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("Close", closes, linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Historical Data"),
                datazoom_opts=[opts.DataZoomOpts()],  # 添加缩放功能
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    min_="dataMin",  # Y 轴最小值
                    max_="dataMax",  # Y 轴最大值
                    splitline_opts=opts.SplitLineOpts(is_show=True)  # 显示分割线
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")  # 显示纵向垂直线
            )
        )
        logger.info(f"Return historical data chart for {symbol} from {start_date} to {end_date} successfully")
        return JsonResponse(line.dump_options_with_quotes(), safe=False)
    except Exception as e:
        logger.error(f"Error generating historical data chart for {symbol} from {start_date} to {end_date}: {e}")
        return render(request, 'error.html', {'error_message': str(e)})

def get_recent_chart(request):
    symbol = request.GET.get('symbol')
    time_range = request.GET.get('time_range')
    print(symbol, time_range)

    try:
        # end date is the latest date in the database
        end_date = RecentData.objects.filter(symbol=symbol).aggregate(max_date=Max('date'))['max_date']
        if time_range == '1d':
            start_date = end_date - timedelta(days=1)
        elif time_range == '3d':
            start_date = end_date - timedelta(days=3)
        elif time_range == '1w':
            start_date = end_date - timedelta(weeks=1)
        elif time_range == '1m':
            start_date = end_date - timedelta(days=30)

        data = RecentData.objects.filter(symbol=symbol, date__range=[start_date, end_date]).order_by('date')
        dates = [d.date.strftime('%Y-%m-%d %H:%M') for d in data]  # 确保日期格式正确
        opens = [d.open for d in data]
        highs = [d.high for d in data]
        lows = [d.low for d in data]
        closes = [d.close for d in data]

        line = (
            Line()
            .add_xaxis(dates)
            .add_yaxis("Open", opens, linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("High", highs, linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("Low", lows, linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("Close", closes, linestyle_opts=opts.LineStyleOpts(width=2), label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Recent Data"),
                datazoom_opts=[opts.DataZoomOpts()],  # 添加缩放功能
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    min_="dataMin",  # Y 轴最小值
                    max_="dataMax",  # Y 轴最大值
                    splitline_opts=opts.SplitLineOpts(is_show=True)  # 显示分割线
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")  # 显示纵向垂直线
            )
        )
        logger.info(f"Return recent data chart for {symbol} of {time_range} successfully")
        return JsonResponse(line.dump_options_with_quotes(), safe=False)
    except Exception as e:
        logger.error(f"Error generating recent data chart for {symbol} of {time_range}: {e}")
        return render(request, 'error.html', {'error_message': str(e)})