from django.views.generic import CreateView, ListView, FormView
from .forms import ExpenseLedgerForm, ExpenseLedgerTransactionForm
from .models import ExpenseLedger, ExpenseLedgerTransaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404

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
class ExpenseBookTransactionView(LoginRequiredMixin, FormView):
    login_url = "/login/"
    form_class = ExpenseLedgerTransactionForm
    success_url = "/"
    template_name = "expense_record/expense_ledger_transaction_form.html"


    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        print(kwargs)
        kwargs['business'] = self.request.user
        return kwargs
    
    def form_valid(self, form):


        expense_ledger = None

        # get expense ledger
        if form.cleaned_data["select_expense_ledger"]:
            expense_ledger = get_object_or_404(ExpenseLedger, business=self.request.user, name=form.cleaned_data["select_expense_ledger"])
        

        # check for empty transactions
        if not form.cleaned_data["amount"] or float(form.cleaned_data["amount"]) < 0.00:
            messages.warning(self.request, "Can not make empty transactions!")
            return self.form_invalid(form)
        

        try:

            # create the transaction
            ExpenseLedgerTransaction.objects.create(
                business=self.request.user,
                expense_ledger=expense_ledger,
                description=form.cleaned_data["description"] or "Cash",
                date=form.cleaned_data["date"],
                debit=float(form.cleaned_data["amount"]),
            )

            return redirect("expense_record:expense-book-transaction")
        except Exception as e:
            print(str(e))
            messages.error(self.request, f"Error: {str(e)}")
            return self.form_invalid(form)