from django.urls import path
from .views import LedgerListView, TransactionListView, CreateNewLedgerView

urlpatterns = [
    path('ledgers/', LedgerListView.as_view(), name='ledger-list'),
    path('transactions/<int:pk>/', TransactionListView.as_view(), name='ledger-transaction-list'),
    path('create-ledger/', CreateNewLedgerView.as_view(), name="create-ledger")
]