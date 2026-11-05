from django.urls import path
from . import views

urlpatterns = [
    path("", views.trade_list, name="trade_list"),
    path("add/", views.trade_create, name="trade_create"),
    path("<int:pk>/edit/", views.trade_edit, name="trade_edit"),
    path("<int:pk>/delete/", views.trade_delete, name="trade_delete"),
    path("analysis/", views.analysis, name="analysis"),
    path("export/", views.export_csv, name="export_csv"),
    path("api/lookup/", views.lookup_company, name="lookup_company"),
]
