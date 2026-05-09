from django.contrib import admin
from .models import HistoricalData, RecentData

# Register your models here.
admin.site.register(HistoricalData)
admin.site.register(RecentData)