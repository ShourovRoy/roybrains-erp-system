from django.contrib import admin
from .models import ExpenseBook, ExpenseTransaction
# Register your models here.

admin.site.register(ExpenseBook)
admin.site.register(ExpenseTransaction)