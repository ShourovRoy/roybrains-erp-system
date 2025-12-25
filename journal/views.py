from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect 
from .models import JournalBook, JournalTransaction
# Create your views here.


class CreateJournalRecord(LoginRequiredMixin, TemplateView):
    login_url = "/login/"
    template_name = "journal/"


    
