from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CashBook
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

