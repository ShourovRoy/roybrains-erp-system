from django.urls import path
from .views import InventoryView, InventoryDetailView, InventoryUpdateView

urlpatterns = [
    path('inventory/', InventoryView.as_view(), name='inventory'),
    path('inventory/detail/<int:pk>/', InventoryDetailView.as_view(), name='inventory_detail'),
    path('inventory/detail/<int:pk>/edit/', InventoryUpdateView.as_view(), name='inventory_update'),
]
