from django.views.generic import ListView, CreateView
from .models import Ledger, Transaction as TransactionLedger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Value
from django.db.models.functions import Coalesce
from .forms import LedgerForm
from django.shortcuts import redirect
from django.contrib import messages
# Create your views here.

class LedgerListView(LoginRequiredMixin, ListView):
    
    model = Ledger
    template_name = 'ledger/ledger-list.html'
    context_object_name = 'ledgers'
    login_url = "/login/"


    def get_queryset(self):

        query = self.request.GET.get('ledger_search_q', '')

        ledger = []

        if query:
            
            ledger = super().get_queryset().annotate(
                similarity=TrigramSimilarity('account_name', query) + TrigramSimilarity(Coalesce('address', Value('')), query) + TrigramSimilarity(Coalesce('branch', Value('')), query)
                + TrigramSimilarity(Coalesce('phone_number', Value('')), query)
            ).filter(
                business=self.request.user,
                similarity__gt=0.2,
            )

        else:
            ledger = super().get_queryset().filter(business=self.request.user).order_by('-created_at')

        return ledger
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        
        if self.request.GET.get('ledger_search_q'):
            context['searched'] = True
        
        return context



class TransactionListView(LoginRequiredMixin, ListView):
    model = TransactionLedger
    template_name = 'ledger/transactions-list.html'
    context_object_name = 'transactions'
    login_url = "/login/"
    paginate_by = 50


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ledger_id'] = int(self.kwargs['pk'])

        return context


    def get_queryset(self):

        if self.request.GET.get('from') and self.request.GET.get('to'):
            l_list = TransactionLedger.objects.filter(
                business=self.request.user,
                ledger=int(self.kwargs['pk']),
                date__date__range=[self.request.GET.get('from'), self.request.GET.get('to')]
            ).order_by('date')
        else:
            l_list = TransactionLedger.objects.filter(business=self.request.user, ledger=int(self.kwargs['pk'])).order_by('date')

        return l_list
    

class CreateNewLedgerView(LoginRequiredMixin, CreateView):
    login_url = "/login/"
    model = Ledger
    template_name = "ledger/create-ledger.html"
    form_class = LedgerForm
    success_url = "create-ledger"

    def form_valid(self, form):

        form.instance.business = self.request.user
        form.instance.note = "Just created without any transaction."

        form.save()
        messages.success(request=self.request, message=f"Ledger of {form.instance.account_name} has been created as {form.instance.account_type} account.")
        return redirect("create-ledger")
        

