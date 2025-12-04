from django.contrib import admin
from .models import CashBook, CashTransaction
# Register your models here.


admin.site.register(CashBook)
admin.site.register(CashTransaction)