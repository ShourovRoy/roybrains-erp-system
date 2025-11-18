from django.views.generic import ListView
from .models import Ledger, Transaction as TransactionLedger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import TrigramSimilarity
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
            ledger = Ledger.objects.annotate(
            similarity=TrigramSimilarity('account_name', query) + TrigramSimilarity('address', query) + TrigramSimilarity('phone_number', query)
        ).filter(
            business=self.request.user,
            similarity__gt=0.2,
        ).order_by('-similarity')
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