from django.urls import path
from .views import LedgerListView, TransactionListView

urlpatterns = [
    path('ledgers/', LedgerListView.as_view(), name='ledger-list'),
    path('transactions/<int:pk>/', TransactionListView.as_view(), name='ledger-transaction-list'),
]