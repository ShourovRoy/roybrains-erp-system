from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.


class InternalBankingControlPanelView(TemplateView):
    template_name = 'internal_banking/control-panel.html'
