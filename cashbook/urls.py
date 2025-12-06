from django.urls import path
from .views import CashbookListView

app_name = "cashbook"
urlpatterns = [
    path("cashbook-panel/", CashbookListView.as_view(), name="cashbook-control-panel")
]