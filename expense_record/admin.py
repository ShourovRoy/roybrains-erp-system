from django.contrib import admin
from .models import ExpenseLedger, ExpenseLedgerTransaction
# Register your models here.

admin.site.register(ExpenseLedger)
admin.site.register(ExpenseLedgerTransaction)