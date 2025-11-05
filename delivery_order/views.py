from django.shortcuts import render
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ledger.models import Ledger
# Create your views here.

class SaleManagementView(LoginRequiredMixin, ListView):
    template_name = 'delivery_order/sale-management.html'
    model = Ledger
    login_url = '/login/'
    context_object_name = 'accounts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.GET.get("account_search", None):
            context['searched'] = True

        return context

    def get_queryset(self):
        query = self.request.GET.get('account_search', None)
        if query:
            return super().get_queryset().filter(account_name__icontains=query, account_type='Customer')
        return []


# TODO: work here
class CreateDeliveryOrderView(LoginRequiredMixin, TemplateView):
    template_name = "delivery_order/create-delivery-order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message"] = "Hello world"
        return context