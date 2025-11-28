from django.urls import path
from .views import CashbookControlPanelView

app_name = "cashbook"
urlpatterns = [
    path("cashbook-panel/", CashbookControlPanelView.as_view(), name="cashbook-control-panel")
]