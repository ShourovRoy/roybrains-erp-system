from django.contrib import admin
from .models import Ledger, Transaction
# Register your models here.

admin.site.register(Ledger)
admin.site.register(Transaction)
