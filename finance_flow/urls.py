from django.urls import path
from .views import FinanceFlowView

urlpatterns = [
    path('finance-flow/', FinanceFlowView.as_view(), name="finance-flow")
]