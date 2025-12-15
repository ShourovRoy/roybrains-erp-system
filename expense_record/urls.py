from django.urls import path
from .views import CreateExpenseBook, ExpenseBookListView

app_name = "expense_record"
urlpatterns = [
    path('create-expense-book/', CreateExpenseBook.as_view(), name='create-expense-book'),
    path('expense-books-list/', ExpenseBookListView.as_view(), name='expense-books-list'),
]