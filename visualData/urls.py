from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.history_data, name='history'),
    path('recent/', views.recent_data, name='display'),
    path('get_historical_chart/', views.get_historical_chart, name='get_historical_chart'),
    path('get_recent_chart/', views.get_recent_chart, name='get_recent_chart'),
]