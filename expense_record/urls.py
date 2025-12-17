from django.urls import path
from .views import CreateExpenseLedger, ExpenseBookListView, ExpenseBookTransactionView

app_name = "expense_record"
urlpatterns = [
    path('create-expense-ledger/', CreateExpenseLedger.as_view(), name='create-expense-ledger'),
    path('expense-books-list/', ExpenseBookListView.as_view(), name='expense-books-list'),
    path('expense-books-transaction/', ExpenseBookTransactionView.as_view(), name='expense-book-transaction'),
]