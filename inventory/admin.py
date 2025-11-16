from django.contrib import admin
from .models import Inventory, SalesLog
# Register your models here.

class QuestionAdmin(admin.ModelAdmin):
    search_fields = ["product_name", 'weight', 'business' ]
    list_display = ["business", "product_name", "weight", "unit_label", "quantity", ]
    sortable_by = ["business", "product_name", "weight", "unit_label", "quantity", ]


admin.site.register(Inventory, QuestionAdmin)
admin.site.register(SalesLog)