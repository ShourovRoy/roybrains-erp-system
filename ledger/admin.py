from django.contrib import admin
from .models import Ledger, Transaction
# Register your models here.

class LedgerAdmin(admin.ModelAdmin):
    search_fields = ["account_name", 'phone_number', 'address', 'account_type' ]
    list_display = ["account_name", "phone_number", "account_type", "status", "note", "balance" ]
    sortable_by = ["created_at", "updated_at", "account_name", "balance" ]

admin.site.register(Ledger, LedgerAdmin)
admin.site.register(Transaction)
