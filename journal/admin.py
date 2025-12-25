from django.contrib import admin
from .models import JournalBook, JournalTransaction
# Register your models here.

admin.site.register(JournalBook);
admin.site.register(JournalTransaction);