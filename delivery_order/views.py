from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ledger.models import Ledger
from inventory.models import Inventory
from .models import DeliveryOrder
from django.shortcuts import redirect
from .forms import DeliveryOrderForm, DeliveryOrderItemFormSet
from django.db import transaction
from django.contrib import messages
from django.contrib.postgres.search import TrigramSimilarity
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


class CreateDeliveryOrderView(LoginRequiredMixin, CreateView):
    template_name = "delivery_order/create-delivery-order.html"
    login_url = '/login/'
    form_class = DeliveryOrderForm
    model = DeliveryOrder
    success_url = "create_delivery_order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"]= DeliveryOrderItemFormSet(self.request.POST, prefix='items')
        else:
            context["formset"] = DeliveryOrderItemFormSet(prefix='items')
        return context
    
    def form_valid(self, form):
        form.instance.business = self.request.user
        context = self.get_context_data()
        formset = context["formset"]

        with transaction.atomic():

            try:

                self.object = form.save()

                if formset.is_valid():
                    items = formset.save(commit=False)
                    for item in items:
                        item.business = self.request.user
                        item.delivery_order = self.object
                        item.total_weight = item.quantity * item.weight
                        item.total_price = item.price * item.quantity

                        item.save()
            except:
                messages.add_message("Something went wrong")
                
                return self.form_invalid(form)

            return redirect("create_delivery_order")



class SearchInventoryProductView(LoginRequiredMixin, ListView):
    template_name = "delivery_order/partials/search-result.html"
    model = Inventory
    context_object_name = "products"

    def get_queryset(self):
        query = self.request.GET.get("product_search", "")

        if query:
            return super().get_queryset().annotate(similarity=TrigramSimilarity("product_name", query)).filter(similarity__gt=0.2, business=self.request.user).order_by("id")
         
        return []
