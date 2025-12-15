from django.urls import path
from .views import CreateExpenseBook

app_name = "expense_record"
urlpatterns = [
    path('create-expense-book/', CreateExpenseBook.as_view(), name='create-expense-book'),
]