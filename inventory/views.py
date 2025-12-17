from django.views.generic import ListView, DetailView, UpdateView, CreateView
from .models import Inventory, SalesLog
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib.postgres.search import TrigramSimilarity
from django.utils.dateparse import parse_date
from datetime import date
from django.db.models import Sum, F
# Create your views here.

# TODO: create inventory create view
class InventoryCreateView(LoginRequiredMixin, CreateView):
    pass



class InventoryView(LoginRequiredMixin, ListView):
    model = Inventory
    template_name = 'inventory/inventory.html'
    context_object_name = 'inventories'
    login_url = '/login/'

    def get_queryset(self):
        if self.request.GET.get('product_name'):

            query = self.request.GET.get('product_name')
         
            products = super().get_queryset().annotate(
                similarity=TrigramSimilarity('product_name', query),
            ).filter(similarity__gt=0.2, business=self.request.user).order_by('-similarity')

            return products
        
        return super().get_queryset().filter(business=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('product_name'):
            context['searched'] = True
        return context

class InventoryDetailView(LoginRequiredMixin, DetailView):
    model = Inventory
    template_name = 'inventory/inventory-details.html'
    context_object_name = 'inventory'
    login_url = '/login/'

    def get_object(self, queryset = None):
        inventory_id = self.kwargs.get('pk')
        return get_object_or_404(self.model, pk=inventory_id, business=self.request.user)

class InventoryUpdateView(LoginRequiredMixin, UpdateView):

    model = Inventory
    fields = ['quantity']
    template_name = 'inventory/inventory-details.html'
    login_url = '/login/'
    success_url = "/inventory"
    
    def get_queryset(self):
        return super().get_queryset().filter(business=self.request.user)
    
# get the sales log view
class SalesLogView(LoginRequiredMixin, ListView):
    model = SalesLog
    template_name = 'inventory/sales-log.html'
    context_object_name = 'sales_logs'
    login_url = '/login/'

    def get_queryset(self):
        qs = super().get_queryset().filter(business=self.request.user)
        selected_date = self.request.GET.get("date")

        # If no date is provided → use today's date
        if not selected_date:
            selected_date = date.today().isoformat()

        parsed_date = parse_date(selected_date)

        if parsed_date:
            qs = qs.filter(date__date=parsed_date)

        return qs.order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        selected_date = self.request.GET.get(
            "date", 
            date.today().isoformat()
        )

        # Keep selected date in the form
        context["selected_date"] = selected_date

        parsed_date = parse_date(selected_date)

        total_sales_price = (
            SalesLog.objects.filter(business=self.request.user, date__date=parsed_date).aggregate(
                total=Sum('price'),
            ) or 0.00
        )['total']


        context["total_sales_price"] = total_sales_price

        return context
