from django.urls import path
from .views import AddCapitalView, SearchBankListView

app_name = 'capital_management'
urlpatterns = [
    path('add/', AddCapitalView.as_view(), name='add_capital'),
    path('search-banks/', SearchBankListView.as_view(), name='search_banks'),
]