from django.urls import path
from .views import CapitalDepositWithdrawView, SearchBankListView

app_name = 'capital_management'
urlpatterns = [
    path('capital/deposite-withdraw/', CapitalDepositWithdrawView.as_view(), name='capital_deposite_withdraw'),
    path('search-banks/', SearchBankListView.as_view(), name='search_banks'),
]