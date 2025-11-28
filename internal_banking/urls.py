from django.urls import path
from .views import InternalBankingControlPanelView, InternalBankingWithdraw, InternalBankingDeposite

urlpatterns = [
    path('internal-banking/control-panel/', InternalBankingControlPanelView.as_view(), name='internal_banking_control_panel'),
    path('internal-banking/withdraw/<int:bank_id>/', InternalBankingWithdraw.as_view(), name='internal_banking_withdraw'),
    path('internal-banking/deposite/<int:bank_id>/', InternalBankingDeposite.as_view(), name='internal_banking_deposite'),
]