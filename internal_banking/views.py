from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from ledger.models import Ledger, Transaction as LedgerTransaction
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from datetime import datetime
from django.db import transaction
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
            return self.form_invalid(form);
    

        try:
            date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
        except Exception as e:
            print(e)
            messages.error(request=self.request, message="Invalid date!")
            return self.form_invalid(form);


        if withdraw_amount < 1:
            messages.warning(request=self.request, message="You can't make empty transaction!")
            return self.form_invalid(form) 



        bank_details_ledger = get_object_or_404(Ledger, business=self.request.user, pk=bank_id)

        # if we are withdrawing then it will credit from the bank balance in out book
        with transaction.atomic():
            self.model.objects.create(
                business=self.request.user,
                ledger=bank_details_ledger,
                credit=withdraw_amount,
                debit=0.0,
                description="withdrawn",
                date=date_time
            )

            # TODO: debit the cashbook

            messages.success(request=self.request, message=f"{withdraw_amount} from {bank_details_ledger.account_name} has been withdrawn.")
            return redirect("internal_banking_withdraw", bank_details_ledger.pk)
        
