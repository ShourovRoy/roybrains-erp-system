from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

class CashbookControlPanelView(LoginRequiredMixin,TemplateView):
    template_name = 'cashbook/control_panel.html'
    login_url = '/login/'

