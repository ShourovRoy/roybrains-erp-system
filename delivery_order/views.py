from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class SaleManagementView(TemplateView):
    template_name = 'delivery_order/sale.html'
