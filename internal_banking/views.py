from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from ledger.models import Ledger, Transaction as LedgerTransaction
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from utils.helper import encode_date_time, get_cashbook_on_date_or_previous
from cashbook.models import CashTransaction
from utils.helper import get_or_create_journal_book
from journal.models import JournalTransaction
# Create your views here.

# Internal banking control panel view
class InternalBankingControlPanelView(LoginRequiredMixin, ListView):
    login_url = "/login/"
    template_name = 'internal_banking/control-panel.html'
    model = Ledger
    context_object_name = "banks"

    def get_queryset(self):

        query = self.request.GET.get("search_bank", None)

        if query:
            return self.model.objects.filter(business=self.request.user, account_name__icontains=query).exclude(branch=None)

        return self.model.objects.filter(business=self.request.user).exclude(branch=None)
    
# Internal banking withdraw view
class InternalBankingWithdraw(LoginRequiredMixin, CreateView, DetailView):
    login_url = "/login/"
    model = LedgerTransaction
    fields = []
    context_object_name = "bank_details"
    template_name = "internal_banking/internal-banking-withdraw.html"

    def get_object(self, queryset = ...):

        bank_id = int(self.kwargs["bank_id"])

        return get_object_or_404(Ledger, business=self.request.user, pk=bank_id)
    

    def form_valid(self, form):

        bank_id = int(self.kwargs["bank_id"])

        withdraw_amount = float(self.request.POST.get("withdraw_amount", 0.0));
        date_time = self.request.POST.get("datetime", None)

        if date_time is None:
            messages.error(request=self.request, message="Date is required!")
            return redirect("internal_banking_withdraw", bank_id)
    

        try:
            date_time = encode_date_time(date_time)
        except Exception as e:
            print(e)
            messages.error(request=self.request, message="Invalid date!")
            return redirect("internal_banking_withdraw", bank_id)

        # check empty transactions
        if withdraw_amount < 1 or withdraw_amount == 0.0:
            messages.warning(request=self.request, message="You can't make empty transaction!")
            return redirect("internal_banking_withdraw", bank_id)
        
        # bank details
        bank_details_ledger = get_object_or_404(Ledger, business=self.request.user, pk=bank_id)

        # check if withdraw amount is available
        if bank_details_ledger.balance < withdraw_amount or bank_details_ledger == 0.0:
            messages.error(request=self.request, message="Insufficiant balance in bank!")
            return redirect("internal_banking_withdraw", bank_details_ledger.pk)


        # if we are withdrawing then it will credit from the bank balance in out book
        try:
            with transaction.atomic():

                # get cash book
                cash_book = get_cashbook_on_date_or_previous(business=self.request.user, date=date_time.date())
                
                self.model.objects.create(
                    business=self.request.user,
                    ledger=bank_details_ledger,
                    credit=withdraw_amount,
                    debit=0.0,
                    description="Cash",
                    date=date_time
                )

                # credit the cashbook bank
                CashTransaction.objects.create(
                    business=self.request.user,
                    cashbook=cash_book,
                    description=f"Cash ({bank_details_ledger.account_name.capitalize()} - {bank_details_ledger.branch})",
                    credit=withdraw_amount,
                    debit=0.00,
                    is_bank=True,
                    date=date_time,
                )

                # debit the cashbook cash
                CashTransaction.objects.create(
                    business=self.request.user,
                    cashbook=cash_book,
                    description=f"{bank_details_ledger.account_name.capitalize()} - {bank_details_ledger.branch}",
                    debit=withdraw_amount,
                    credit=0.00,
                    is_bank=False,
                    date=date_time,
                )

                # get journal book
                journal_book = get_or_create_journal_book(business=self.request.user, date=date_time.date())


                # update journal
                # cash debit
                JournalTransaction.objects.create(
                    business=self.request.user,
                    journal=journal_book,
                    date=date_time.date(),
                    credit=0.00,
                    debit=float(withdraw_amount),
                    description=f"Cash",
                )
                
                # bank credit
                JournalTransaction.objects.create(
                    business=self.request.user,
                    journal=journal_book,
                    date=date_time.date(),
                    ledger_ref=bank_details_ledger,
                    debit=0.00,
                    credit=float(withdraw_amount),
                    description=f"{bank_details_ledger.account_name.capitalize()} - {bank_details_ledger.branch}",
                )

                
                # udpate the cashbook balance
                cash_book.cash_amount += withdraw_amount
                cash_book.bank_amount -= withdraw_amount

                cash_book.save()

                messages.success(request=self.request, message=f"{withdraw_amount} from {bank_details_ledger.account_name} has been withdrawn.")
                return redirect("internal_banking_withdraw", bank_details_ledger.pk)

        except Exception as e:
            print(e)
            messages.error(request=self.request.user, message=f"Error occoured: {str(e)}")
            return redirect("internal_banking_withdraw", bank_details_ledger.pk)
            
        
# Internal banking deposite
class InternalBankingDeposite(LoginRequiredMixin, CreateView, DetailView):
    login_url = "/login/"
    model = LedgerTransaction
    fields = []
    context_object_name = "bank_details"
    template_name = "internal_banking/internal-banking-deposite.html"



    def get_object(self, queryset = ...):

        bank_id = int(self.kwargs["bank_id"])

        return get_object_or_404(Ledger, business=self.request.user, pk=bank_id)
    

    def form_valid(self, form):

        bank_id = int(self.kwargs["bank_id"])

        deposite_amount = float(self.request.POST.get("deposite_amount", 0.0));
        date_time = self.request.POST.get("datetime", None)

        if date_time is None:
            messages.error(request=self.request, message="Date is required!")
            return redirect("internal_banking_deposite", bank_id)
    

        try:
            date_time = date_time = encode_date_time(date_time)
        except Exception as e:
            print(e)
            messages.error(request=self.request, message="Invalid date!")
            return redirect("internal_banking_deposite", bank_id)


        if deposite_amount < 1:
            messages.warning(request=self.request, message="You can't make empty transaction!")
            return redirect("internal_banking_deposite", bank_id) 



        bank_details_ledger = get_object_or_404(Ledger, business=self.request.user, pk=bank_id)

        try:
            # if we are withdrawing then it will credit from the bank balance in out book
            with transaction.atomic():

                # get cash book
                cash_book = get_cashbook_on_date_or_previous(business=self.request.user, date=date_time.date())


                # check if the cash is avialable in the cashbook to deposit into the bank
                if deposite_amount > cash_book.cash_amount:
                    raise ValueError(f"{deposite_amount} amount is not available in the cashbook cash!")

                self.model.objects.create(
                    business=self.request.user,
                    ledger=bank_details_ledger,
                    debit=deposite_amount,
                    credit=0.0,
                    description="Cash",
                    date=date_time
                )

                # debit the cashbook bank
                CashTransaction.objects.create(
                        business=self.request.user,
                        cashbook=cash_book,
                        description=f"Cash ({bank_details_ledger.account_name.capitalize()} - {bank_details_ledger.branch})",
                        debit=deposite_amount,
                        credit=0.00,
                        is_bank=True,
                        date=date_time,
                    )

                # credit the cashbook cash
                CashTransaction.objects.create(
                        business=self.request.user,
                        cashbook=cash_book,
                        description=f"{bank_details_ledger.account_name.capitalize()} - {bank_details_ledger.branch}",
                        credit=deposite_amount,
                        debit=0.00,
                        is_bank=False,
                        date=date_time,
                )

                # get journal book
                journal_book = get_or_create_journal_book(business=self.request.user, date=date_time.date())
                
                # create journal entry
                # bank debit
                JournalTransaction.objects.create(
                    business=self.request.user,
                    journal=journal_book,
                    date=date_time.date(),
                    ledger_ref=bank_details_ledger,
                    debit=float(deposite_amount),
                    credit=0.00,
                    description=f"{bank_details_ledger.account_name.capitalize()} - {bank_details_ledger.branch}",
                )
 
                # cash credit
                JournalTransaction.objects.create(
                    business=self.request.user,
                    journal=journal_book,
                    date=date_time.date(),
                    debit=0.00,
                    credit=float(deposite_amount),
                    description=f"Cash",
                )

                # udpate the cashbook balance
                cash_book.cash_amount -= deposite_amount
                cash_book.bank_amount += deposite_amount

                cash_book.save()

                messages.success(request=self.request, message=f"{deposite_amount} at {bank_details_ledger.account_name} has been despiste.")
                return redirect("internal_banking_deposite", bank_details_ledger.pk)
            

        except Exception as e:
            print(e)
            messages.error(request=self.request, message=f"Error: {str(e)}")
            return redirect("internal_banking_deposite", bank_details_ledger.pk)
