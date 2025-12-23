from django.views.generic import CreateView, ListView, FormView
from .forms import ExpenseLedgerForm, ExpenseLedgerTransactionForm
from .models import ExpenseLedger, ExpenseLedgerTransaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum, F
from datetime import date
from ledger.models import Ledger, Transaction as LedgerTransaction
from django.contrib.postgres.search import TrigramSimilarity
from utils.helper import get_cashbook_on_date_or_previous
from cashbook.models import CashTransaction

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
        kwargs['business'] = self.request.user
        return kwargs
    
    def form_valid(self, form):


        expense_ledger = None
        bank_ledger = None
        is_bank_transfered = False


        # get lastest cashbook
        cash_book = get_cashbook_on_date_or_previous(self.request.user, form.cleaned_data["date"].date())


        # check for empty transactions
        if not form.cleaned_data["amount"] or float(form.cleaned_data["amount"]) < 0.00:
            messages.warning(self.request, "Can not make empty transactions!")
            return self.form_invalid(form)
        

        # get expense ledger
        if form.cleaned_data["select_expense_ledger"]:
            expense_ledger = get_object_or_404(ExpenseLedger, business=self.request.user, name=form.cleaned_data["select_expense_ledger"])
        

        # check if the expense source is bank
        if form.cleaned_data["expense_source"] == "bank" :
            bank_ledger = get_object_or_404(Ledger, business=self.request.user, pk=form.cleaned_data["bank_id"])
            is_bank_transfered = form.cleaned_data["is_bank_transfered"] or False

            # check the bank balance
            if bank_ledger.balance < float(form.cleaned_data["amount"]) or bank_ledger.balance == 0.00:
                messages.error(self.request, f"{bank_ledger.account_name} has not enough balance!")
                return self.form_invalid(form)
            
        else:

            # for cash check if cash available or not in cashbook
            if cash_book.cash_amount < float(form.cleaned_data["amount"]):
                messages.error(self.request, f"You don't have enough cash!")
                return self.form_invalid(form)
        

        try:

            with transaction.atomic():
                expense_desc = None

                # if expense done using direct bank transfer
                if bank_ledger and is_bank_transfered:

                    # bank ledger credit 
                    LedgerTransaction.objects.create(
                        business=self.request.user,
                        ledger=bank_ledger,
                        description=f"{expense_ledger.name.capitalize()} Expense.",
                        debit=0.00,
                        credit=float(form.cleaned_data["amount"]),
                        date=form.cleaned_data["date"],
                    )

                    # credit the cashbook bank transaction for making expense
                    CashTransaction.objects.create(
                        business=self.request.user,
                        cashbook=cash_book,
                        description=f"{expense_ledger.name.capitalize()} Expense.",
                        is_bank=True,
                        credit=float(form.cleaned_data["amount"]),
                        debit=0.00,
                        date=form.cleaned_data["date"],
                    )

                    expense_desc = f"{bank_ledger.account_name.capitalize()} - {bank_ledger.branch}"

                    # update bank and cash balance in cashbook
                    cash_book.bank_amount -= float(form.cleaned_data["amount"])

                # if expense done by withdrawing from bank
                if bank_ledger and is_bank_transfered == False:

                    # bank ledger credit
                    LedgerTransaction.objects.create(
                        business=self.request.user,
                        ledger=bank_ledger,
                        description=f"Cash",
                        debit=0.00,
                        credit=float(form.cleaned_data["amount"]),
                        date=form.cleaned_data["date"],
                    )


                    # bank credit transaction in cashbook 
                    CashTransaction.objects.create(
                        business=self.request.user,
                        cashbook=cash_book,
                        description=f"Cash",
                        is_bank=True,
                        credit=float(form.cleaned_data["amount"]),
                        debit=0.00,
                        date=form.cleaned_data["date"],
                    )

                    # cash debit transaction in cashbook
                    CashTransaction.objects.create(
                        business=self.request.user,
                        cashbook=cash_book,
                        description=f"{bank_ledger.account_name.capitalize()} - {bank_ledger.branch}",
                        is_bank=False,
                        debit=float(form.cleaned_data["amount"]),
                        credit=0.00,
                        date=form.cleaned_data["date"],
                    )

                    # cash credit for expense in cashbook
                    CashTransaction.objects.create(
                        business=self.request.user,
                        cashbook=cash_book,
                        description=f"{expense_ledger.name.capitalize()} Expense",
                        is_bank=False,
                        credit=float(form.cleaned_data["amount"]),
                        debit=0.00,
                        date=form.cleaned_data["date"],
                    )

                    # udpate the expense description
                    expense_desc = f"Cash"

                    # update bank and cash balance in cashbook
                    cash_book.bank_amount -= float(form.cleaned_data["amount"])


                # for cash only expense without bank involvement
                if not bank_ledger:
                    # cash credit for expense in cashbook
                    CashTransaction.objects.create(
                        business=self.request.user,
                        cashbook=cash_book,
                        description=f"{expense_ledger.name.capitalize()} Expense",
                        is_bank=False,
                        credit=float(form.cleaned_data["amount"]),
                        debit=0.00,
                        date=form.cleaned_data["date"],
                    )

                    # udpate the expense description
                    expense_desc = f"Cash"

                    # deduct cash balance from cashbook 
                    cash_book.cash_amount -= float(form.cleaned_data["amount"])



                # create the transaction
                ExpenseLedgerTransaction.objects.create(
                    business=self.request.user,
                    expense_ledger=expense_ledger,
                    description=expense_desc,
                    date=form.cleaned_data["date"],
                    debit=float(form.cleaned_data["amount"]),
                )


                # save cashbook
                cash_book.save()


                messages.success(self.request, "Expense made.")

                return redirect("expense_record:expense-book-transaction")
            


        except Exception as e:
            print(str(e))
            messages.error(self.request, f"Error: {str(e)}")
            return self.form_invalid(form)
        

# Expense detail view 
class ExpenseDetailsView(LoginRequiredMixin, ListView):
    login_url = "/login/"
    template_name = "expense_record/expense_details_transaction_list.html"
    model = ExpenseLedgerTransaction
    context_object_name = "expense_transactions"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        expense_book_id = self.kwargs["pk"];

        self.expense_ledger = get_object_or_404(ExpenseLedger, business=self.request.user, pk=expense_book_id)
          
        return super().dispatch(request, *args, **kwargs)


    def get_queryset(self):

        if self.request.GET.get("start_date") and self.request.GET.get("end_date"):


            return super().get_queryset().filter(
                business=self.request.user, 
                expense_ledger=self.expense_ledger,
                date__date__range=[self.request.GET.get('start_date'), self.request.GET.get('end_date')]
                ).order_by('date', 'id')
        else:
            return super().get_queryset().filter(
                business=self.request.user, 
                expense_ledger=self.expense_ledger,
                ).order_by('date', 'id')



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        

        expense_transactions = self.object_list

        # life time expense 
        life_time_expense = (ExpenseLedgerTransaction.objects.filter(
            business=self.request.user,
            expense_ledger=self.expense_ledger,
        ).order_by('date', 'id').aggregate(
            total=Sum(F("debit") - F("credit"))
        )["total"] or 0.00)



        # if filtered
        if self.request.GET.get("start_date") and self.request.GET.get("end_date"):
            context.update({
                "filtered": True
            })
            today_expense = (expense_transactions.aggregate(
                total=Sum(F("debit") - F("credit"))
            )["total"] or 0.00)
        else:

            # per day expense
            today_expense = (ExpenseLedgerTransaction.objects.filter(
                business=self.request.user,
                expense_ledger=self.expense_ledger,
                date__date=date.today()
            ).aggregate(
                total=Sum(F("debit") - F("credit"))
            )["total"] or 0.00)

        # per year expense
        yearly_expense = (ExpenseLedgerTransaction.objects.filter(
                business=self.request.user,
                expense_ledger=self.expense_ledger,
                date__year=date.today().year
            ).aggregate(
            total=Sum(F("debit") - F("credit"))
        )["total"] or 0.00)


        context.update({
            "expense_details": self.expense_ledger,
            "life_time_expense": life_time_expense,
            "today_expense": today_expense,
            "yearly_expense": yearly_expense,
            "today": str(date.today())
        })

        return context


# search expense 
class ExpenseBankSearch(LoginRequiredMixin, ListView):
    login_url = "/login/"
    model = Ledger
    context_object_name = "banks"
    template_name = "expense_record/partials/expense_bank_search_result.html"


    def get_queryset(self):

        query = self.request.GET.get("bank_search", None)


        if not query:
            return super().get_queryset().filter(business=self.request.user, similarity__gt=0.3, branch__isnull=False).exclude(branch="").order_by("updated_at")

        return super().get_queryset().annotate(
                similarity=TrigramSimilarity("account_name", query),
            ).filter(business=self.request.user, similarity__gt=0.3, branch__isnull=False, ).exclude(branch="").order_by("-similarity")
