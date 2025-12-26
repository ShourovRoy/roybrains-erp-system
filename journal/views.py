from django.views.generic import ListView 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect 
from .models import JournalBook, JournalTransaction
# Create your views here.


class JournalBookList(LoginRequiredMixin, ListView):
    login_url = "/login/"
    template_name = "journal/journal-books.html"
    model = JournalBook
    context_object_name = "journals"


    def get_queryset(self):
        return super().get_queryset().filter(business=self.request.user).order_by("-date")


    
