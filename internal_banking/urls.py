from django.urls import path
from .views import InternalBankingControlPanelView

urlpatterns = [
    path('internal-banking/control-panel/', InternalBankingControlPanelView.as_view(), name='internal_banking_control_panel'),
]