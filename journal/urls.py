from django.urls import path
from .views import CreateJournalRecord


app_name = "journal"
urlpatterns = [
    path("create-journal-record/", CreateJournalRecord.as_view(), name="create-journal-record")
]