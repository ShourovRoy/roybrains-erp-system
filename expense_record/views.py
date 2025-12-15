from django.views.generic import CreateView
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


    def form_valid(self, form):
        form.instance.business = self.request.user
        messages.success(self.request, 'Expense Book Created Successfully')
        return super().form_valid(form)