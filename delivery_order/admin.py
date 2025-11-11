from django.contrib import admin
from .models import DeliveryOrder, DeliveryOrderItem
# Register your models here.

admin.site.register(DeliveryOrder)
admin.site.register(DeliveryOrderItem)
