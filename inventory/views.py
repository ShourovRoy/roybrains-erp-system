from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from .models import Inventory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.postgres.search import TrigramSimilarity
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
    
