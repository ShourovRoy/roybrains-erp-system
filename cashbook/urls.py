from django.urls import path
from .views import CashbookListView, CashbookDetailView

app_name = "cashbook"
urlpatterns = [
    path("cashbook-panel/", CashbookListView.as_view(), name="cashbook-control-panel"),
    path("cashbook-panel/cashbook-details/<int:pk>/", CashbookDetailView.as_view(), name="cashbook-detail"),
]