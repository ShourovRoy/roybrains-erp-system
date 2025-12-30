from django.shortcuts import get_object_or_404
from django.views.generic import ListView , DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect 
from .models import JournalBook, JournalTransaction
# Create your views here.

# journal book dist view
class JournalBookList(LoginRequiredMixin, ListView):
    login_url = "/login/"
    template_name = "journal/journal-books.html"
    model = JournalBook
    context_object_name = "journals"


    def get_queryset(self):
        return super().get_queryset().filter(business=self.request.user).order_by("-date")


# journal book details view
class JournalBookDetailsView(LoginRequiredMixin, DeleteView):
    login_url = "/login"
    model = JournalBook
    template_name = "journal/journal-details.html"
    context_object_name = "journal_details"


    def dispatch(self, request, *args, **kwargs):
        journal_id = self.kwargs["pk"]

        self.journal_book = get_object_or_404(JournalBook, pk=int(journal_id), business=self.request.user)

        return super().dispatch(request, *args, **kwargs)


    def get_object(self, queryset = None):
        return self.journal_book
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        journals = JournalTransaction.objects.filter(
            business=self.request.user,
            journal=self.journal_book,
        ).order_by("-date", "id")

        context["journals"] = journals

        

        return context

