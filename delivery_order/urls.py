from django.urls import path
from .views import SaleManagementView
urlpatterns = [
    path('sale/', SaleManagementView.as_view(), name='sale_management'),
]