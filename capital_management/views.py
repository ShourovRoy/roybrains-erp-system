from django.shortcuts import redirect
from django.views.generic import ListView, FormView
from .models import Capital, CapitalTransaction
from .forms import CapitalForm
from django.contrib.auth.mixins import LoginRequiredMixin
from ledger.models import Ledger
from django.db import transaction
from django.contrib import messages
from utils.helper import get_cashbook_on_date_or_previous, encode_date_time
# Create your views here.

class AddCapitalView(LoginRequiredMixin, FormView):
    template_name = 'capital_management/capital-control-panel.html'
    form_class = CapitalForm
    login_url = "/login/"
    success_url = "/add/"

    def form_valid(self, form):
        # Add any custom processing here if needed
       
        print("Capital Form Validated:", form.cleaned_data)

        bank_details = None

        if form.cleaned_data['invest_in'] == 'bank' and form.cleaned_data['bank_account_id']:
            try:
                bank_details = Ledger.objects.get(id=form.cleaned_data['bank_account_id'], business=self.request.user)
            except Ledger.DoesNotExist:
                bank_details = None
                messages.error(self.request, "Invalid bank account selected.")
                return self.form_invalid(form)
            
        try:

            # TODO: 8-12-25 start from here, if bank is present it should create bank transaction else cash transaction. and update the capital accordingly.

            with transaction.atomic():

                if bank_details:
                    print(bank_details)
                else:
                    cash_book = get_cashbook_on_date_or_previous(self.request.user, encode_date_time(form.cleaned_data['date']))
                    print("Using Cash Book:", cash_book)


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