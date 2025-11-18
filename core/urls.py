from django.contrib import admin
from django.urls import path, include
from .views import HomeView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name="home"),
    path('', include('inventory.urls')),
    path('', include('business.urls')),
    path('', include('purchase_record.urls')),
    path('', include('delivery_order.urls')),
    path('', include('ledger.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
