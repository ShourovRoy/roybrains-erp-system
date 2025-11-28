from django.urls import path
from .views import InternalBankingControlPanelView, InternalBankingWithdraw

urlpatterns = [
    path('internal-banking/control-panel/', InternalBankingControlPanelView.as_view(), name='internal_banking_control_panel'),
    path('internal-banking/withdraw/<int:bank_id>/', InternalBankingWithdraw.as_view(), name='internal_banking_withdraw'),
]