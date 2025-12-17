from django.urls import path
from .views import CreateExpenseType, ExpenseBookListView, ExpenseBookTransactionView

app_name = "expense_record"
urlpatterns = [
    path('create-expense-type/', CreateExpenseType.as_view(), name='create-expense-type'),
    path('expense-books-list/', ExpenseBookListView.as_view(), name='expense-books-list'),
    path('expense-books-transaction/', ExpenseBookTransactionView.as_view(), name='expense-book-transaction'),
]