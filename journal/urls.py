from django.urls import path
from .views import JournalBookList, JournalBookDetailsView


app_name = "journal"
urlpatterns = [
    path("journal-books-list/", JournalBookList.as_view(), name="journal-books-list"),
    path("journal-details/<int:pk>/", JournalBookDetailsView.as_view(), name="journal-details")
]