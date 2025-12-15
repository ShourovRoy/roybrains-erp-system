from django.views.generic import CreateView, ListView
from .forms import ExpenseBookForm
from .models import ExpenseBook
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# Create your views here.
# create a expense book
class CreateExpenseBook(LoginRequiredMixin, CreateView):
    model = ExpenseBook
    form_class = ExpenseBookForm
    template_name = "expense_record/expense_book_form.html"
    success_url = "create-expense-book"
    login_url = '/login/'


    def form_valid(self, form):
        form.instance.business = self.request.user
        messages.success(self.request, 'Expense Book Created Successfully')
        return super().form_valid(form)
    

# expense ledger list view
class ExpenseBookListView(LoginRequiredMixin, ListView):
    login_url = "/login/"
    model = ExpenseBook
    template_name = "expense_record/expense-books.html"
    context_object_name = "exepnse_books"


    def get_queryset(self):
        return super().get_queryset().filter(business=self.request.user).order_by("created_at", "id")
    