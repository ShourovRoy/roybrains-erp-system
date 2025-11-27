from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ledger.models import Ledger, Transaction as LedgerTransaction
# Create your views here.


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
