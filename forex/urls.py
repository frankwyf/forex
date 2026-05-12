from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("visual/", include("visualData.urls")),
    path("favicon.ico", RedirectView.as_view(url="/static/favicon.svg", permanent=True)),
    path("", RedirectView.as_view(url="/visual/history/", permanent=False)),
]
