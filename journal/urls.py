from django.urls import path
from .views import JournalBookList 


app_name = "journal"
urlpatterns = [
    path("journal-books-list/", JournalBookList.as_view(), name="journal-books-list")
]