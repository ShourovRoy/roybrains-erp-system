from django.urls import path
from .views import FinanceFlowView, FincialAccountSearchView, FinancialInflowView, FinancialCashInFlow, FinancialBankInFlow, FinancialBankInflowActionView

urlpatterns = [
    path('finance-flow/', FinanceFlowView.as_view(), name="finance-flow"),
    path('search-accounts', FincialAccountSearchView.as_view(), name="finance-flow-search"),
    path('financial-inflow/<int:pk>', FinancialInflowView.as_view(), name="financial-inflow"),
    path('financial-inflow/cash-deposite/<int:pk>', FinancialCashInFlow.as_view(), name="financial-inflow-cash"),
    path('financial-inflow/bank-deposite/<int:pk>', FinancialBankInFlow.as_view(), name="financial-inflow-bank"),
    path('financial-inflow/bank-deposite/<int:pk>/<int:bank_id>', FinancialBankInflowActionView.as_view(), name="financial-inflow-bank-action"),
]