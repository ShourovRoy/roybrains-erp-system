from django.contrib import admin
from .models import PurchaseVoucher, PurchaseItem
# Register your models here.

admin.site.register(PurchaseVoucher)
admin.site.register(PurchaseItem)
