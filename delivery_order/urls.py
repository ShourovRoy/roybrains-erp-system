from django.urls import path
from .views import SaleManagementView, CreateDeliveryOrderView
urlpatterns = [
    path('sale/', SaleManagementView.as_view(), name='sale_management'),
    path('create-delivery-order/',  CreateDeliveryOrderView.as_view(), name="create_delivery_order")
]