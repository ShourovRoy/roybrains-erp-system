from django.shortcuts import redirect
from django.views.generic import ListView, FormView
from .models import Capital, CapitalTransaction
from .forms import CapitalForm
from django.contrib.auth.mixins import LoginRequiredMixin
from ledger.models import Ledger, Transaction as LedgerTransaction
from django.db import transaction
from django.contrib import messages
from utils.helper import get_cashbook_on_date_or_previous, encode_date_time
from cashbook.models import CashTransaction
# Create your views here.

class CapitalDepositWithdrawView(LoginRequiredMixin, FormView):
    template_name = 'capital_management/capital-control-panel.html'
    form_class = CapitalForm
    login_url = "/login/"
    success_url = '/capital/deposite-withdraw/'

    def form_valid(self, form):
        # Add any custom processing here if needed
       
        

        bank_details = None

        if form.cleaned_data['invest_in'] == 'bank' and form.cleaned_data['bank_account_id']:
            try:
                bank_details = Ledger.objects.get(id=form.cleaned_data['bank_account_id'], business=self.request.user)
            except Ledger.DoesNotExist:
                bank_details = None
                messages.error(self.request, "Invalid bank account selected.")
                return self.form_invalid(form)
            
        try:

            # start transaction block to invest and withdraw capital in cashbook and bank ledger account

            with transaction.atomic():

                date_time = encode_date_time(form.cleaned_data['date'])

                capital_obj, capital_created = Capital.objects.get_or_create(
                    business=self.request.user,
                    defaults={
                        'balance': 0.0,
                    }
                )


                # handle bank capital
                if bank_details:

                    # create bank ledger transaction
                    LedgerTransaction.objects.create(
                        business=self.request.user,
                        ledger=bank_details,
                        description=f"Capital Investment" if form.cleaned_data['transaction_type'] == 'deposit' else f"Capital Withdrawal",
                        debit=float(form.cleaned_data['amount']) if form.cleaned_data['transaction_type'] == 'deposit' else 0.00,
                        credit= float(form.cleaned_data['amount']) if form.cleaned_data['transaction_type'] == 'withdrawal' else 0.00,
                        date=date_time
                    )
                    
                    # create capital transaction
                    CapitalTransaction.objects.create(
                        business=self.request.user,
                        capital=capital_obj,
                        debit=float(form.cleaned_data['amount']) if form.cleaned_data['transaction_type'] == 'withdrawal' else 0.00,
                        credit=float(form.cleaned_data['amount']) if form.cleaned_data['transaction_type'] == 'deposit' else 0.00,
                        description=f"Capital Investment at Bank - {bank_details.account_name}" if form.cleaned_data['transaction_type'] == 'deposit' else f"Capital Withdrawal from Bank - {bank_details.account_name}",
                        date=date_time,
                    )

                    # get latest cash book
                    cash_book = get_cashbook_on_date_or_previous(self.request.user, encode_date_time(form.cleaned_data['date']))

                    # create cash transaction for bank capital
                    CashTransaction.objects.create(
                        business=self.request.user,
                        cashbook=cash_book,
                        description=f"Capital Investment via Bank - {bank_details.account_name}",
                        is_bank=True,
                        debit=float(form.cleaned_data['amount']) if form.cleaned_data['transaction_type'] == 'deposit' else 0.00,
                        credit=float(form.cleaned_data['amount']) if form.cleaned_data['transaction_type'] == 'withdrawal' else 0.00,
                        date=date_time
                    )


                    # update cash book bank amount
                    if form.cleaned_data['transaction_type'] == 'deposit':
                        cash_book.bank_amount += float(form.cleaned_data['amount'])
                    else:
                        cash_book.bank_amount -= float(form.cleaned_data['amount'])

                    cash_book.save()
                
                # handle cash capital
                else:

                    # create capital transaction
                    CapitalTransaction.objects.create(
                        business=self.request.user,
                        capital=capital_obj,
                        debit=float(form.cleaned_data['amount']) if form.cleaned_data['transaction_type'] == 'withdrawal' else 0.00,
                        credit=float(form.cleaned_data['amount']) if form.cleaned_data['transaction_type'] == 'deposit' else 0.00,
                        description="Capital Investment in cash" if form.cleaned_data['transaction_type'] == 'deposit' else "Capital Withdrawal in cash",
                        date=date_time,
                    )


                    cash_book = get_cashbook_on_date_or_previous(self.request.user, encode_date_time(form.cleaned_data['date']))
                    

                    # create cash transaction for cash book
                    CashTransaction.objects.create(
                        business=self.request.user,
                        cashbook=cash_book,
                        description=f"Capital Investment via Cash",
                        is_bank=False,
                        debit=float(form.cleaned_data['amount']) if form.cleaned_data['transaction_type'] == 'deposit' else 0.00,
                        credit=float(form.cleaned_data['amount']) if form.cleaned_data['transaction_type'] == 'withdrawal' else 0.00,
                        date=date_time
                    )


                    # update cash book cash amount
                    if form.cleaned_data['transaction_type'] == 'deposit':
                        cash_book.cash_amount += float(form.cleaned_data['amount'])
                    else:
                        cash_book.cash_amount -= float(form.cleaned_data['amount'])

                    cash_book.save()

            return super().form_valid(form)
        
        except Exception as e:
            print("Error processing capital transaction:", e)
            return self.form_invalid(form)
            
   

# search bank list view
class SearchBankListView(LoginRequiredMixin, ListView):
    template_name = 'capital_management/partials/bank-search-list.html'
    login_url = "/login/"
    model = Ledger
    context_object_name = 'banks'

    def get_queryset(self):
        q = self.request.GET.get('search_query', None)

        if q is not None:
            return self.model.objects.filter(business=self.request.user, account_type='Bank', account_name__icontains=q).order_by('updated_at')
        
        return super().get_queryset().none()