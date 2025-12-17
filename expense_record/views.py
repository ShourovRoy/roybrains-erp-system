from django.views.generic import CreateView, ListView, TemplateView
from .forms import ExpenseLedgerForm
from .models import ExpenseLedger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError
from django.urls import reverse_lazy

# Create your views here.
# create a expense book
class CreateExpenseLedger(LoginRequiredMixin, CreateView):
    model = ExpenseLedger
    form_class = ExpenseLedgerForm
    template_name = "expense_record/expense_ledger_form.html"
    success_url = reverse_lazy("expense_record:create-expense-ledger")
    login_url = '/login/'


    def form_valid(self, form):
        try:
            form.instance.business = self.request.user
            
            form_response = super().form_valid(form)
            messages.success(self.request, 'Expense Book Created Successfully')
            return form_response
        except IntegrityError as e:
            print(str(e))
            messages.error(self.request, 'Expense type already exist!')
            return self.form_invalid(form)

    

# expense ledger list view
class ExpenseBookListView(LoginRequiredMixin, ListView):
    login_url = "/login/"
    model = ExpenseLedger
    template_name = "expense_record/expense-books.html"
    context_object_name = "exepnse_books"


    def get_queryset(self):
        return super().get_queryset().filter(business=self.request.user).order_by("created_at", "id")


# Expense ledger transactions
class ExpenseBookTransactionView(LoginRequiredMixin, TemplateView):
    pass