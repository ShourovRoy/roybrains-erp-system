from django.urls import path
from .views import SaleManagementView, CreateDeliveryOrderView, SearchInventoryProductView, DeliveryOrdersList
urlpatterns = [
    path('sale/', SaleManagementView.as_view(), name='sale_management'),
    path('create-delivery-order/',  CreateDeliveryOrderView.as_view(), name="create_delivery_order"),
    path('search-inventory-products/', SearchInventoryProductView.as_view(), name="search_inventory_products"),
    path('delivery-orders-list/', DeliveryOrdersList.as_view(), name="delivery_orders_list"),
]