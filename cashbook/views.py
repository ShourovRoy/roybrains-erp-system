from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CashBook, CashTransaction
from django.shortcuts import get_object_or_404
# Create your views here.


# Cashbook Control Panel View
class CashbookListView(LoginRequiredMixin, ListView):
    template_name = 'cashbook/cashbook-list.html'
    login_url = '/login/'
    model = CashBook
    context_object_name = 'cashbooks'
    paginate_by = 10


    def get_queryset(self):
        return super().get_queryset().filter(business=self.request.user).order_by('-date')
    

# Cashbook Detail View with transactions list
class CashbookDetailView(LoginRequiredMixin, DetailView):
    template_name = "cashbook/cashbook-details.html"
    login_url = "/login/"
    model = CashBook
    context_object_name = "cashbook_details"


    def get_object(self, queryset = None):
        return get_object_or_404(self.model, business=self.request.user, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['entries'] = CashTransaction.objects.filter(business=self.request.user, cashbook=self.get_object()).order_by('date')
        return context